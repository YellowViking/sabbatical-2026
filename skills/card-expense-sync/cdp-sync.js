// Bank pull driven from the PERSISTENT CDP browser instead of the Playwright one.
//
// Run each half inside the matching bank tab with chrome-devtools-cdp `evaluate_script`:
//   CHASE_PULL  -> in a secure.chase.com tab
//   AMEX_PULL   -> in a global.americanexpress.com tab
//
// Why: the Playwright MCP browser restarts often and silently drops its cookie jar, so a login
// there rarely survives to the next tool call. The CDP browser (see
// ../google-sheets-edit/cdp-up.sh) persists, so one sign-in there lasts until the bank's own
// ~20-minute server-side expiry.
//
// Both fetches are SAME-ORIGIN from the bank's own page, so no CORS issue and no request
// context needed. Results are POSTed to the sink, which now sends Access-Control-Allow-Origin.

// ---------------------------------------------------------------- CHASE ----
// Paste as the `function` arg while a secure.chase.com tab is selected.
async () => {
  const CFG = await (await fetch('http://127.0.0.1:8899/config')).json();
  const BASE = '/svc/rr/accounts/secure/gateway/credit-card/transactions' +
               '/inquiry-maintenance/etu-transactions/v4/accounts/transactions';
  const out = {};
  for (const a of CFG.chase) {
    const all = []; let cursor = null;
    for (let i = 0; i < 25; i++) {
      let qs = `digital-account-identifier=${a.digitalAccountIdentifier}` +
               `&record-count=100&sort-order-code=D&sort-key-code=T`;
      if (cursor) qs += `&pagination-contextual-text=${encodeURIComponent(cursor)}`;
      const r = await fetch(`${BASE}?${qs}`, { credentials: 'include' });
      if (r.status !== 200) return { error: `chase HTTP ${r.status}`, got: all.length };
      const j = await r.json();
      const acts = j.activities || [];
      all.push(...acts);
      const oldest = acts.length ? acts[acts.length - 1].transactionDate : null;
      cursor = j.paginationContextualText;
      if (!j.moreRecordsIndicator || !cursor || (oldest && oldest < CFG.sinceISO)) break;
    }
    out[a.label] = all;
  }
  await fetch('http://127.0.0.1:8899/chase', {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(out),
  });
  return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v.length]));
}

// ----------------------------------------------------------------- AMEX ----
// Paste as the `function` arg while a global.americanexpress.com tab is selected.
async () => {
  const CFG = await (await fetch('http://127.0.0.1:8899/config')).json();
  const H = { 'content-type': 'application/json', accept: 'application/json', 'ce-source': 'WEB' };
  const out = {};
  for (const a of CFG.amex) {
    let txns = [], periods = [], j;
    for (let k = 0; k < 3; k++) {            // Amex sometimes 200s with an empty list
      const r = await fetch('https://functions.americanexpress.com/ReadAccountActivity.web.v1', {
        method: 'POST', credentials: 'include', headers: H,
        body: JSON.stringify({ accountToken: a.accountToken, axplocale: 'en-US',
          transactionFilters: { limit: 100, offset: 1 }, view: 'RECENT' }),
      });
      if (r.status !== 200) return { error: `amex HTTP ${r.status}` };
      j = await r.json();
      txns = (j.activityData?.data || []).flatMap((g) => g.transactions || []);
      periods = j.statementPeriods || [];
      if (txns.length) break;
      await new Promise((res) => setTimeout(res, 1500));
    }
    if (!txns.length) return { error: 'amex returned 0 transactions 3x' };
    const u = (x) => `/api/servicing/v1/financials/documents` +
                     `?account_key=${a.accountKey}&file_format=csv&client_id=AmexAPI${x}`;
    const csvParts = [await (await fetch(u(''), { credentials: 'include' })).text()];
    for (const p of periods) {
      if (p.cycleIndex === 0 || p.endDate < CFG.sinceISO) continue;
      csvParts.push(await (await fetch(u(`&statement_end_date=${p.endDate}`),
        { credentials: 'include' })).text());
    }
    out[a.label] = { transactions: txns, statementPeriods: periods, csvParts };
  }
  await fetch('http://127.0.0.1:8899/amex', {
    method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(out),
  });
  return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, v.transactions.length]));
}
