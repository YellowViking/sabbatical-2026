// Run in a secure.chase.com tab. Driven by cdp-sync.mjs, which passes the accounts JSON in as `cfgStr`.
async (cfgStr) => {
  const CFG = JSON.parse(cfgStr);
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
  return out;
}
