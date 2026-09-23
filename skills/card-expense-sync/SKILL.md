---
name: card-expense-sync
description: >
  Pull Amex and Chase credit-card transactions via cookie-authenticated REST
  calls (no CSV download dialogs, no click-loops), categorise them into
  Food&Drink / Lodging / Transportation / Other with MCC codes, amortise hotel
  charges across nights, and emit paste-ready week blocks for the "Expense 2022
  Roadtrip" Google Sheet. Use for the sabbatical expense catch-up, or any time
  the user asks "what have I spent" / "update the expense sheet". Requires a
  Playwright/Chrome profile already signed in to both banks.
---

# Credit-card → expense-sheet sync

## What this is

Three stages, each independently re-runnable:

1. **`sync.js`** — pulls raw activity from both banks over REST into
   `~/Documents/sabbatical-finance/raw/sync-<ts>.json`.
2. **`categorize.py`** — turns that into `sheet-rows.csv` (one row per day) plus
   `transactions-classified.csv` (the audit trail).
3. **`build_blocks.py`** → **`../google-sheets-edit/paste.js`** — renders week
   blocks and pastes them into the sheet.

**Never put any of this data in the repo.** `~/sabbatical` is a *public* GitHub
repo. Raw payloads, `accounts.json`, and the derived CSVs all live under
`~/Documents/sabbatical-finance/`. The skill scripts are safe to commit; the
account identifiers are not.

## Setup

`~/Documents/sabbatical-finance/accounts.json` holds the identifiers:

```json
{ "sinceISO": "2026-08-01",
  "chase": [{ "label": "Sapphire Preferred", "digitalAccountIdentifier": "…" }],
  "amex":  [{ "label": "Platinum Card", "accountToken": "…", "accountKey": "…" }] }
```

Re-discover them if they ever break:
- **Chase** — sign in, click the card on the dashboard, read the URL:
  `/dashboard/summary/<digitalAccountIdentifier>/CARD/BAC`
- **Amex** — `GET https://global.americanexpress.com/api/servicing/v1/member/accounts?client_id=AmexAPI`
  (cookie auth) → `account_token`, `account_key`

## Running a sync

```bash
python3 skills/card-expense-sync/sink.py &     # localhost:8899
```

Then, in a browser signed in to **both** banks:

```
browser_run_code_unsafe { filename: "skills/card-expense-sync/sync.js" }
```

```bash
cd ~/Documents/sabbatical-finance
python3 ~/sabbatical/skills/card-expense-sync/categorize.py --start 2026-08-24 --end <today>
```

## The endpoints

Both banks authenticate on **cookies alone** — no CSRF token, no bearer header.
Use `page.context().request`, Playwright's APIRequestContext: it shares the
browser's cookie jar across origins, so one script reaches both banks no matter
which page is in front, and it is not subject to CORS.

### Chase — GET, paginated

```
GET https://secure.chase.com/svc/rr/accounts/secure/gateway/credit-card/transactions
    /inquiry-maintenance/etu-transactions/v4/accounts/transactions
    ?digital-account-identifier=<ID>&record-count=100&sort-order-code=D&sort-key-code=T
```

- `record-count` **caps at 100** (asking for more is a 400 that tells you so).
- Page backwards by feeding the response's `paginationContextualText` back in as
  `pagination-contextual-text`. Other spellings 403. Stop on `moreRecordsIndicator: false`.
- Returns `activities[]` with `transactionDate`, `transactionAmount`,
  `transactionStatusCode` (Posted/Pending), `creditDebitCode`, and
  `merchantDetails.rawMerchantDetails` → `merchantDbaName`, `merchantCityName`,
  `merchantCountryCode`, **`merchantCategoryCode`** (the MCC — this is what makes
  reliable categorisation possible; the CSV export has none of it).
- Amounts are **unsigned**; direction is in `creditDebitCode` (`D`/`C`).
- `merchantCountryCode` is alpha-2 on posted rows but **numeric ISO-3166 on
  pending ones** (`578`=NO, `752`=SE, `208`=DK…). Map both.

### Amex — POST for JSON, GET for CSV

```
POST https://functions.americanexpress.com/ReadAccountActivity.web.v1
{ "accountToken": "…", "axplocale": "en-US",
  "transactionFilters": { "limit": 100, "offset": 1 }, "view": "RECENT" }
```

- Headers: `content-type: application/json`, `accept: application/json`, `ce-source: WEB`.
- `view` accepts `RECENT` only as far as probing shows — `DATE_RANGE` and
  `STATEMENT` both 400. `RECENT` ≈ the current statement cycle.
- Response: `activityData.data[].transactions[]` with `displayDate`,
  `displayDescription`, `transactionAmount.amount` (**already signed** — do not
  re-negate credits), `status`, and `categoryCode`
  (`C7` Restaurant, `C8` Transportation, `C9` Travel, `C3` Entertainment, `C5` Merchandise).
- `statementPeriods[]` gives every cycle's `startDate`/`endDate`/`cycleIndex`.

```
GET https://global.americanexpress.com/api/servicing/v1/financials/documents
    ?account_key=<KEY>&file_format=csv&client_id=AmexAPI
    [&start_date=…&end_date=… | &statement_end_date=…]
```

Returns `Date,Description,Amount` only — no MCC, no country. Useful as a
cross-check, not as the primary source. `start_date`/`end_date` only filter
*within* the current cycle; to reach a closed cycle pass that cycle's
`statement_end_date`. `file_format` also takes `excel`, `quickbooks`, `quicken`.

## Traps

- **Amex disables `eval`** on its pages, so Playwright's `page.evaluate` fails
  there with "eval is disabled". Use `page.context().request` instead — it never
  touches page JS. (This is also why `sync.js` runs entirely through the request
  context.)
- **The `browser_run_code_unsafe` sandbox has no `require`, `fs`, `process`, or
  `URLSearchParams`.** It cannot read config or write files. That is what
  `sink.py` is for: it serves `accounts.json` at `/config` and accepts the result
  as a POST, so raw bank data goes straight to disk without passing through the
  agent's context. Build query strings by hand.
- **Warm the session before believing a 401.** After the MCP browser restarts, the request
  context can 401 on both banks even though the cookies are fine. Navigating to
  `secure.chase.com/web/auth/dashboard` / `global.americanexpress.com/activity/recent` once
  and waiting a few seconds revives it. Only if the page itself lands on a **login screen**
  is the session actually dead. Check `page.title()` — "Accounts - chase.com" means in,
  "Sign in - chase.com" means out.
- Amex sessions die much faster than Chase's; expect to re-auth Amex alone on a repeat sync.
- Sessions expire quickly. If a pull returns a login page, re-authenticate in the
  browser and re-run — `sync.js` is idempotent.
- The sandbox has no `setTimeout` either — use `await page.waitForTimeout(ms)` for delays.

## Categorisation

`categorize.py` classifies from the MCC (Chase) or `categoryCode` (Amex), with a
short `OVERRIDES` list for the cases where the code lies:

| Merchant | Filed as | Actually |
|---|---|---|
| `PAYPAL *DONKEY` (Donkey Republic bikes) | 7999 misc | Transportation |
| `FOODORA` | 4816 digital services | Food&Drink |
| `7-ELEVEN` on Amex | C5 Merchandise | Food&Drink |
| `HOSTELLING INT` | 7011 | Lodging (membership bought to unlock the rate) |

`EXCLUDE` drops non-trip spend (Linode, Uber One, Walmart, and any statement
credit that offsets it).

`RECLASS` fixes **hotel incidentals billed under the property's own MCC 7011**. A hostel
laundry charge reads as lodging and then gets amortised across the whole stay, inflating every
night and hiding a real Other cost. Match on amount so the actual room charge is untouched:

```python
("City Hostel Stockholm", 15.69, OTHER),   # laundry, not a room charge
```

Suspect this whenever a stay has **two charges from the same property** and one is small and
odd-sized — ask rather than assume it is a room fee.

**Lodging is amortised across nights** — this is how the historical sheet is
written, and it is the single most important transformation. One 135.37 hotel
charge becomes 45.12 on each of three nights rather than a spike on the booking
date. Edit the `STAYS` table when a new stay is booked:

```python
("BKG*HOTEL", 308.07, "2026-09-02", 4)   # substring, exact amount or None, first night, nights
```

Two ways this rule table goes wrong silently, both seen in practice:

- **Match on amount, not charge date**, when one merchant bills twice the same day.
  The two Booking.com charges are otherwise indistinguishable, and a date-only rule
  swapped a 1-night and a 4-night stay.
- **Match the property, not the OTA.** Both Stockholm stays billed as
  `AGODA.COM …`, so a bare `AGODA` rule claimed whichever charge it saw first and
  amortised it over the wrong nights. Use `CITY HOSTE` / `STF STOCKH`.

And the one that is hardest to spot: **re-check `nights` whenever the route
changes.** Bergen was booked as 6 nights but cut to 2 when the Sep 8 BGO→ARN
flight went in, which quietly spread the stay at $23.93/night instead of $71.81.
The charge is the tell — if amount ÷ nights looks too cheap for the city, the
night count is stale, not the price.

`COUNTRY_TIMELINE` drives the sheet's Country column. Do **not** derive it from
merchant country: Booking.com bills from NL, Agoda from DE, Hostelling
International from GB.

## Cash and award redemptions

Neither reaches the card feeds, and both are easy to lose. Keep them in the
script, not typed into the sheet — a later sync regenerates the grid and would
silently overwrite anything hand-entered.

`CASH` — spend the cards never saw, converted via `FX`:

```python
("2026-08-31", "Laundry (Oslo, day 2)", 250, "NOK", OTHER),
```

`POINTS` — award redemptions, valued at `CPP` cents per point and amortised over
their nights. **Value every redemption or none**; valuing the hotel but not the
flights inflates Lodging relative to Transportation and makes the trip look
cheaper than it is. Current convention: Hyatt **1.7¢**, airline points **1.4¢**.

```python
("2026-08-27", "Hyatt Place Gothenburg (award)", 7500 * 3, "HYATT", LODGING, 3),
```

Points rows are emitted **already split per night** and carry `preSpread: True`.
`spread()` must skip them — otherwise it re-amortises each of the N per-night
rows across N nights again and the stay lands N² times.

Award cash fees are separate `CASH` rows on the same date as the redemption, so
the fee and the point value read together (the SEA–CPH ticket was
25,500 Virgin Points **+ $5.60**; both sit on Aug 24).

## Writing to the sheet — use the sheet's own macro

The spreadsheet has a bound Apps Script macro, **Extensions > Macros > "new week"**
(`Cmd+Opt+Shift+1`). **Always create blocks with it. Never hand-build one.**

```js
function newweek() {                          // Recorded Macros (Expense 2022 Roadtrip)
  WeeklyTemplate.copyTo(getActiveRange(), PASTE_NORMAL, false);  // Weeks!I180:O190
  getCurrentCell().setValue('Week ' + ++CurrentWeek);            // Metadata!B1
  currentWeekRange.setValue(CurrentWeek);
}
```

It does three things a manual paste does not: stamps the template *with its
Currency and Country dropdowns*, labels the week, and advances
`Metadata!CurrentWeek`. A hand-built block silently loses all three.

**Check `Metadata!CurrentWeek` against the last block's `Week N` label before
running it** — they drift when weeks get added by hand. Set the counter to the
real last week first, or the macro will emit colliding numbers.

Procedure:

1. Find the last used row by reading the sheet tail **in the formula bar** (gviz
   drops rows, so its row numbers do not match the grid). The next block starts
   2 rows after the last grand-total row; blocks then repeat every 12 rows.
2. Reconcile `Metadata!CurrentWeek` with the last `Week N` label.
3. Select the anchor cell and fire the macro, once per week block.
4. ```bash
   python3 build_blocks.py --first-row <row> \
           --sheet-url "https://docs.google.com/spreadsheets/d/<ID>/edit?gid=0#gid=0"
   ```
5. `browser_run_code_unsafe { filename: "skills/google-sheets-edit/paste.js" }`

Step 5 pastes the numbers, restores the number format, then **types** the country
values — see `../google-sheets-edit/SKILL.md` for why typing is required.

### Country dropdown

Country cells validate against the `Countries` **named range** (`Metadata!B2:B26`)
with *reject input*, so a country missing from that list is silently refused and a
modal blocks every later keystroke. Denmark, Sweden, Norway, Finland, Estonia,
Latvia, Lithuania, Slovenia, Croatia, Italy, Netherlands and Germany were appended
for this trip. To add more: extend the list on `Metadata`, then widen the
`Countries` named range via **Data > Named ranges** — editing the validation rule
itself is unnecessary and wrong, since it just points at the name.
