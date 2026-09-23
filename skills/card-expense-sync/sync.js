// Pull raw card activity from Amex + Chase using cookie-authenticated REST calls.
//
// Run with the Playwright MCP tool:
//   browser_run_code_unsafe { filename: "<repo>/skills/card-expense-sync/sync.js" }
//
// Requires:
//  1. A Chrome/Playwright context already signed in to BOTH global.americanexpress.com
//     and secure.chase.com. No clicking, no CSV download dialogs, no page JS (Amex disables eval()).
//     Everything goes through page.context().request, which shares the browser's cookie jar across
//     origins, so one script reaches both banks regardless of which page is in front.
//  2. `python3 sink.py` running — the sandbox this executes in has no require/fs/process, so it
//     cannot read config or write files. It POSTs the result to the sink, which persists it to
//     ~/Documents/sabbatical-finance/raw/ — OUTSIDE the public git repo.

async (page) => {
  const api = page.context().request;
  const SINK = 'http://127.0.0.1:8899';

  // Config is fetched over HTTP rather than read from disk (no fs in this sandbox).
  const CFG = await (await api.get(`${SINK}/config`)).json();
  const JSON_H = { 'content-type': 'application/json', accept: 'application/json', 'ce-source': 'WEB' };
  const log = [];

  // ---------------------------------------------------------------- Chase --
  // GET, cookie auth only. record-count caps at 100; page backwards by feeding
  // the previous response's `paginationContextualText` into `pagination-contextual-text`.
  const CHASE_TXN =
    'https://secure.chase.com/svc/rr/accounts/secure/gateway/credit-card/transactions' +
    '/inquiry-maintenance/etu-transactions/v4/accounts/transactions';

  async function chaseAll(acctId, sinceISO) {
    const all = [];
    let ctx = null;
    for (let pageNo = 0; pageNo < 25; pageNo++) {
      // NB: no URLSearchParams in this sandbox — build the query string by hand.
      let qs =
        `digital-account-identifier=${encodeURIComponent(acctId)}` +
        `&record-count=100&sort-order-code=D&sort-key-code=T`; // descending, by transaction date
      if (ctx) qs += `&pagination-contextual-text=${encodeURIComponent(ctx)}`;
      const r = await api.get(`${CHASE_TXN}?${qs}`);
      if (r.status() !== 200) {
        log.push(`chase ${acctId} page ${pageNo}: HTTP ${r.status()} ${(await r.text()).slice(0, 200)}`);
        break;
      }
      const j = JSON.parse(await r.text());
      const acts = j.activities || [];
      all.push(...acts);
      const oldest = acts.length ? acts[acts.length - 1].transactionDate : null;
      ctx = j.paginationContextualText;
      if (!j.moreRecordsIndicator || !ctx || (oldest && oldest < sinceISO)) break;
    }
    return all;
  }

  const chase = {};
  for (const a of CFG.chase || []) {
    const acts = await chaseAll(a.digitalAccountIdentifier, CFG.sinceISO || '2026-08-01');
    chase[a.label] = acts;
    log.push(`chase ${a.label}: ${acts.length} activities`);
  }

  // ----------------------------------------------------------------- Amex --
  // Two complementary sources:
  //   JSON  POST functions.americanexpress.com/ReadAccountActivity.web.v1  -> categoryCode, status
  //   CSV   GET  /api/servicing/v1/financials/documents?...&file_format=csv -> Date,Description,Amount
  // The CSV honours start_date/end_date, but only WITHIN the current statement cycle unless you
  // also pass statement_end_date. So: pull the current cycle plainly, then one call per closed
  // cycle using its statement_end_date, and merge.
  const amex = {};
  for (const a of CFG.amex || []) {
    const body = {
      accountToken: a.accountToken,
      axplocale: 'en-US',
      transactionFilters: { limit: 100, offset: 1 },
      view: 'RECENT',
    };
    // Amex intermittently answers 200 with an EMPTY activity list on a valid session. Taken at
    // face value that silently drops every Amex charge from the sync, so retry before believing
    // a zero and surface it loudly if it persists.
    let j, txns, periods;
    for (let attempt = 1; attempt <= 3; attempt++) {
      const r = await api.post('https://functions.americanexpress.com/ReadAccountActivity.web.v1', {
        headers: JSON_H,
        data: body,
      });
      j = JSON.parse(await r.text());
      txns = (j.activityData?.data || []).flatMap((g) => g.transactions || []);
      periods = j.statementPeriods || [];
      if (txns.length) break;
      log.push(`amex ${a.label}: empty activity on attempt ${attempt}, retrying`);
      await page.waitForTimeout(1500); // no setTimeout in this sandbox
    }
    if (!txns.length) {
      log.push(`amex ${a.label}: WARNING still 0 transactions — do NOT categorise this sync`);
    }

    // CSV: current cycle + every closed cycle that reaches back past sinceISO.
    const since = CFG.sinceISO || '2026-08-01';
    const csvURL = (extra) =>
      `https://global.americanexpress.com/api/servicing/v1/financials/documents` +
      `?account_key=${a.accountKey}&file_format=csv&client_id=AmexAPI${extra}`;
    const csvParts = [];
    csvParts.push(await (await api.get(csvURL(''))).text());
    for (const p of periods) {
      if (p.cycleIndex === 0 || p.endDate < since) continue;
      csvParts.push(await (await api.get(csvURL(`&statement_end_date=${p.endDate}`))).text());
    }

    amex[a.label] = { transactions: txns, statementPeriods: periods, categories: j.activityData?.categories, csvParts };
    log.push(`amex ${a.label}: ${txns.length} json txns, ${csvParts.length} csv chunks`);
  }

  const saved = await api.post(`${SINK}/sync`, {
    headers: { 'content-type': 'application/json' },
    data: { pulledAt: new Date().toISOString(), chase, amex },
  });
  return JSON.stringify({ sink: await saved.json(), log }, null, 1);
}
