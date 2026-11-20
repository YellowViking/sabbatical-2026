// Run in a global.americanexpress.com tab. Driven by cdp-sync.mjs, which passes the accounts JSON in as `cfgStr`.
async (cfgStr) => {
  const CFG = JSON.parse(cfgStr);
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
  return out;
}
