// ONE-CALL expense refresh: preflight -> pull both banks -> categorise -> write the sheet.
//
//   python3 sink.py &      # once
//   browser_run_code_unsafe { filename: ".../card-expense-sync/refresh.js" }
//
// Why one call: bank sessions expire in ~20 minutes. Splitting the refresh across four tool
// calls let the session age out mid-run, which is what kept forcing re-logins. Everything
// between the two banks and the spreadsheet now happens inside a single browser turn, with the
// Python work delegated to the sink's /process endpoint.
//
// It NEVER navigates an existing tab. Warming and spreadsheet work happen in pages this script
// opens and closes itself, so a tab you just logged into is left alone.

async (page) => {
  const ctx = page.context();
  const api = ctx.request;
  const SINK = 'http://127.0.0.1:8899';
  const log = [];

  const CFG = await (await api.get(`${SINK}/config`)).json();
  const JSON_H = { 'content-type': 'application/json', accept: 'application/json', 'ce-source': 'WEB' };

  const CHASE_PROBE =
    'https://secure.chase.com/svc/rr/accounts/secure/gateway/credit-card/transactions' +
    '/inquiry-maintenance/etu-transactions/v4/accounts/transactions' +
    `?digital-account-identifier=${CFG.chase[0].digitalAccountIdentifier}` +
    '&record-count=1&sort-order-code=D&sort-key-code=T';
  const AMEX_PROBE = 'https://global.americanexpress.com/api/servicing/v1/member/accounts?client_id=AmexAPI';

  // A cold request context 401s even on live cookies. Open a THROWAWAY page to warm it, then
  // re-probe. Only a genuine login screen means the session is actually dead.
  async function ensure(name, probe, warmUrl, loginRe) {
    if ((await api.get(probe)).status() === 200) return { name, ok: true, warmed: false };
    const p = await ctx.newPage();
    try {
      await p.goto(warmUrl, { waitUntil: 'domcontentloaded' });
      await p.waitForTimeout(6000);
      const title = await p.title();
      const ok = (await api.get(probe)).status() === 200;
      return { name, ok, warmed: true, loggedOut: loginRe.test(title), title };
    } finally {
      await p.close();
    }
  }

  const chaseState = await ensure('chase', CHASE_PROBE,
    'https://secure.chase.com/web/auth/dashboard#/dashboard/overview', /sign in/i);
  const amexState = await ensure('amex', AMEX_PROBE,
    'https://global.americanexpress.com/activity/recent', /log ?in/i);

  const dead = [chaseState, amexState].filter((s) => !s.ok);
  if (dead.length) {
    return JSON.stringify({
      stopped: 'AUTH',
      needLogin: dead.map((d) => d.name),
      detail: dead,
      hint: 'Sign in, then re-run this same file. Nothing was written.',
    }, null, 1);
  }

  // ------------------------------------------------------------------ pull --
  const chase = {};
  for (const a of CFG.chase) {
    const all = []; let cursor = null;
    for (let i = 0; i < 25; i++) {
      let qs = `digital-account-identifier=${a.digitalAccountIdentifier}` +
               `&record-count=100&sort-order-code=D&sort-key-code=T`;
      if (cursor) qs += `&pagination-contextual-text=${encodeURIComponent(cursor)}`;
      const r = await api.get(
        'https://secure.chase.com/svc/rr/accounts/secure/gateway/credit-card/transactions' +
        `/inquiry-maintenance/etu-transactions/v4/accounts/transactions?${qs}`);
      if (r.status() !== 200) { log.push(`chase HTTP ${r.status()}`); break; }
      const j = JSON.parse(await r.text());
      const acts = j.activities || [];
      all.push(...acts);
      const oldest = acts.length ? acts[acts.length - 1].transactionDate : null;
      cursor = j.paginationContextualText;
      if (!j.moreRecordsIndicator || !cursor || (oldest && oldest < CFG.sinceISO)) break;
    }
    chase[a.label] = all;
    log.push(`chase ${a.label}: ${all.length}`);
  }

  const amex = {};
  for (const a of CFG.amex) {
    let j, txns = [], periods = [];
    for (let k = 0; k < 3; k++) {          // Amex sometimes 200s with an empty list
      const r = await api.post('https://functions.americanexpress.com/ReadAccountActivity.web.v1',
        { headers: JSON_H,
          data: { accountToken: a.accountToken, axplocale: 'en-US',
                  transactionFilters: { limit: 100, offset: 1 }, view: 'RECENT' } });
      j = JSON.parse(await r.text());
      txns = (j.activityData?.data || []).flatMap((g) => g.transactions || []);
      periods = j.statementPeriods || [];
      if (txns.length) break;
      await page.waitForTimeout(1500);     // no setTimeout in this sandbox
    }
    if (!txns.length) return JSON.stringify({ stopped: 'AMEX_EMPTY', log }, null, 1);
    const u = (x) => 'https://global.americanexpress.com/api/servicing/v1/financials/documents' +
                     `?account_key=${a.accountKey}&file_format=csv&client_id=AmexAPI${x}`;
    const csvParts = [await (await api.get(u(''))).text()];
    for (const p of periods) {
      if (p.cycleIndex === 0 || p.endDate < CFG.sinceISO) continue;
      csvParts.push(await (await api.get(u(`&statement_end_date=${p.endDate}`))).text());
    }
    amex[a.label] = { transactions: txns, statementPeriods: periods, csvParts };
    log.push(`amex ${a.label}: ${txns.length} json, ${csvParts.length} csv`);
  }

  await api.post(`${SINK}/sync`, { headers: { 'content-type': 'application/json' },
    data: { pulledAt: new Date().toISOString(), chase, amex } });

  // --------------------------------------------------------------- process --
  const proc = await api.post(`${SINK}/process`, { headers: { 'content-type': 'application/json' }, data: {} });
  const res = await proc.json();
  if (!res.ok) return JSON.stringify({ stopped: 'PIPELINE', log, detail: res.log }, null, 1);
  const job = res.payload;
  log.push(...res.log);

  // ----------------------------------------------------------------- write --
  const sheet = await ctx.newPage();
  try {
    await sheet.goto(job.url);
    await sheet.waitForTimeout(4000);
    await ctx.grantPermissions(['clipboard-read', 'clipboard-write'], { origin: 'https://docs.google.com' });
    const sel = async (a) => {
      await sheet.evaluate((x) => {
        const nb = document.querySelector('#t-name-box');
        nb.focus(); nb.select();
        document.execCommand('insertText', false, x);
        nb.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
      }, a);
      await sheet.waitForTimeout(700);
    };
    for (const w of job.writes) {
      await sheet.evaluate((t) => navigator.clipboard.writeText(t), w.tsv);
      await sel(w.anchor);
      await sheet.keyboard.press('Meta+V');
      await sheet.waitForTimeout(1500);
    }
    await sel(job.formatFrom);
    await sheet.keyboard.press('Meta+C');
    await sheet.waitForTimeout(900);
    for (const t of job.formatTo) {
      await sel(t); await sheet.keyboard.press('Meta+Alt+V'); await sheet.waitForTimeout(1200);
    }
    await sheet.keyboard.press('Escape');
    // Country cells are dropdowns — typed, never pasted, or the validation is destroyed.
    for (const t of job.types) {
      await sel(t.cell); await sheet.keyboard.type(t.text);
      await sheet.keyboard.press('Enter'); await sheet.waitForTimeout(420);
    }
    const verified = {};
    for (const a of job.verify || []) {
      await sel(a);
      verified[a] = await sheet.evaluate(() =>
        document.querySelector('#t-formula-bar-input').innerText.replace(/\n$/, ''));
    }
    log.push(`wrote ${job.writes.length} blocks, typed ${job.types.length} countries`);
    return JSON.stringify({ ok: true, log, verified }, null, 1);
  } finally {
    await sheet.close();
  }
}
