// Run in a secure.chase.com tab. Driven by cdp-sync.mjs; arg = JSON {cfg, start, end} (YYYYMMDD).
// Chase's "Download account activity" CSV for a date range — the ONLY way to reach a CLOSED
// statement cycle (the JSON transactions API is scoped to the current one). Pure API, no UI:
//   1. POST /svc/rl/accounts/secure/v1/csrf/token/list with header `x-jpmc-csrf-token: NONE`
//      -> {code:"SUCCESS", csrfToken}. (Found by reading Chase's own JS: the app reads the
//      token from this call's cached response; without the NONE header it answers 401.)
//   2. GET …/digital-transaction-activity/v1/transaction-activities?…&csrftoken=<token>
//      — it 500s without csrftoken / submit / eligibility-indicator. Max 1,000 rows per call.
async (arg) => {
  const { cfg, start, end } = JSON.parse(arg);
  const H = { 'x-jpmc-channel': 'id=C30', 'content-type': 'application/x-www-form-urlencoded; charset=UTF-8' };
  const t = await (await fetch('/svc/rl/accounts/secure/v1/csrf/token/list',
    { method: 'POST', credentials: 'include', headers: { ...H, 'x-jpmc-csrf-token': 'NONE' } })).json();
  if (!t.csrfToken) return { error: `csrf token: ${t.code}` };
  const out = {};
  for (const a of JSON.parse(cfg).chase) {
    const qs = `account-activity-download-type-code=CSV&digital-account-identifier=${a.digitalAccountIdentifier}` +
               `&start-date=${start}&end-date=${end}&csrftoken=${encodeURIComponent(t.csrfToken)}` +
               `&submit=Submit&eligibility-indicator=true`;
    const r = await fetch('/svc/rr/accounts/secure/gateway/credit-card/transactions/inquiry-maintenance' +
      '/digital-transaction-activity/v1/transaction-activities?' + qs,
      { credentials: 'include', headers: { ...H, 'x-jpmc-csrf-token': t.csrfToken } });
    const csv = await r.text();
    if (r.status !== 200 || !csv.startsWith('Transaction Date')) return { error: `csv HTTP ${r.status}` };
    out[a.label] = csv;
  }
  return out;
}
