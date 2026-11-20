---
name: card-expense-sync
description: >
  Pull Amex and Chase credit-card transactions via cookie-authenticated REST
  calls (no CSV download dialogs, no click-loops), categorise them into
  Food&Drink / Lodging / Transportation / Other with MCC codes, amortise hotel
  charges across nights, and emit paste-ready week blocks for the "Expense 2022
  Roadtrip" Google Sheet. Use for the sabbatical expense catch-up, or any time
  the user asks "what have I spent" / "update the expense sheet". One command:
  `node skills/card-expense-sync/cdp-sync.mjs --write`, against the persistent
  CDP Chrome signed in to both banks.
---

# Credit-card → expense-sheet sync

## Quick start — one command

```bash
bash skills/google-sheets-edit/cdp-up.sh --no-warm        # persistent Chrome on :9222 (reuses if up)
node skills/card-expense-sync/cdp-sync.mjs --write        # pull, categorise, write, verify
```

That pulls both banks from their own tabs, unions the result into the ledger, prints the last
two complete weeks (Sun–Sat), creates any missing week block **with the sheet's own macro**,
types the figures and countries, and reads each block back to diff it. About 15 s once signed in.

| Flag | Effect |
|---|---|
| `--weeks 74-75` | choose blocks (default: the last two complete weeks — the older one catches late posts) |
| `--no-pull` | re-categorise and re-write from saved syncs only — use after editing `categorize.py` |
| `--banks chase` | pull only Chase (the weekly job's default). Safe: the ledger unions every sync, so a skipped card's charges land whenever it is next pulled |
| `--wait-login 45` | instead of exiting 2, poll every 15 s for sign-in; a pull that fails on a dead session goes back to waiting |
| *(no `--write`)* | dry run: pull + print only |

Exit **2** means a bank needs signing in: the script names which one and leaves its tab on
the login page. Bank sessions die after ~20 minutes, so sign in right before running.

Watch the `⚠ no STAYS rule` lines it prints — each is a lodging charge that landed as a
one-day spike. Read the nights from the booking site (below), add a `STAYS` row, re-run with
`--no-pull --write`.

Needs no browser MCP — it drives Chrome through `../google-sheets-edit/cdp.mjs`.

### Every Chase pull also saves a rolling statement CSV

The JSON API only covers the **current statement cycle** (Chase closes on the 18th). A sync
after a close returned 19 rows and no trace of Oct 11–17. So each Chase pull also fetches
`chase-csv.js`: the last ~75 days as Chase's own CSV, by pure API (csrf token → download
endpoint; recipe in `AGENTS.md`). `categorize.py` then merges:

- CSV rows are matched to Chase JSON rows **one-for-one on (date, amount)**, plus a ±5-day,
  same-name-stem match against *pending* JSON rows, whose dates shift when they post.
  Only the leftovers are added. **Never match on whole days**: a statement boundary splits a
  day between the two sources, and one stray pending $1 once hid a whole day (Agoda prepayment
  + two train tickets).
- Overlapping CSVs: each date comes from the newest file only.
- CSV rows carry Chase's coarse category, not an MCC. `OVERRIDES` beat it (`FLIX`, `MUZEUM`…),
  `"Travel"` maps to Transportation, and lodging names (`HOSTEL`, `SOBE`, `APARTMA`…) win first.
- CSV refunds and credits are kept as negative rows.
- CSV rows have no merchant country, so CSV-only days need a `COUNTRY_TIMELINE` entry.
- This also exposed an old JSON dedup bug: two genuine $9.31 Voi rides on consecutive days had
  been merged into one. The CSV restored the second ride (Week 71 +$9.31).

### ⚠️ The "new week" macro can run late — fire it once, then hands off

On 20 Oct, Apps Script sat on "Running script" for over 90 s. Reading cells meanwhile moved
the selection, a Cancel didn't take, and two retries each bumped `CurrentWeek` (75 → 78). Only
one block landed, but it was stamped "Week 78". `ensureBlock` now fires once, watches only the
banner, checks the label via gviz (which selects nothing), never retries, and verifies the
counter afterwards. If it throws, fix `Weeks!A<row>` and `Metadata!B1` by hand before re-running.

### Weekly job (launchd, hourly check → Sundays from 10:00 local)

launchd's calendar keeps the time zone it booted with (the first runs fired at 19:07 CEST, i.e.
10:07 Pacific), so the plist fires **hourly** and `weekly.sh --scheduled` runs only on Sunday at
or after 10:00 in the Mac's current zone, once per ISO week (stamp file
`~/Documents/sabbatical-finance/.weekly-YYYY-Www`). It pulls **Chase only**.
`weekly.sh` runs the whole thing every Sunday: it brings up the CDP Chrome if needed, opens the
bank tabs, and sends a macOS notification asking you to sign in. With `--wait-login 45` it
then checks every 15 s, and the moment both banks are in it pulls, writes, verifies and
notifies the week total. Output is appended to `~/Documents/sabbatical-finance/weekly.log`.

```bash
bash skills/card-expense-sync/weekly.sh --install   # or --remove; plain = run now
```

It cannot sign in for you, and it cannot read booking sites. When the final notification says
`N lodging charge(s) need a STAYS rule`, an agent still has to read the bookings, add the rows
and re-run `cdp-sync.mjs --no-pull --write`.

## What this is

Three stages, each independently re-runnable:

1. **Pull** — `chase-pull.js` / `amex-pull.js`, run inside the bank tabs by `cdp-sync.mjs`
   (or `sync.js` from a Playwright browser), into
   `~/Documents/sabbatical-finance/raw/sync-<ts>.json`.
2. **`categorize.py`** — turns that into `sheet-rows.csv` (one row per day) plus
   `transactions-classified.csv` (the audit trail).
3. **Write** — `cdp-sync.mjs --write`, or the older `build_blocks.py` →
   `../google-sheets-edit/paste.js` from a Playwright browser.

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

## Running a sync from a Playwright browser (fallback)

Only if the CDP browser is unavailable. `sync.js` uses Playwright's request context, so it
needs the sink to land data on disk:

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

### Why the CDP path never touches the sink

⚠️ **A bank page can no longer reach `127.0.0.1`** (Chrome 153 Local Network Access; Amex's
CSP blocks it outright). Any design where the *page* fetches the sink fails with a bare
"Failed to fetch". `cdp-sync.mjs` passes the config in as the eval argument, takes the data
back as the return value, and writes the sync file itself.

Never POST `{}` to the sink's `/sync` to "test" it — that writes a real, empty `sync-*.json`
that `build_ledger()` will read.

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
## ⚠️ One sync is not a history — the ledger is

**Chase's JSON endpoint is hard-scoped to the CURRENT statement cycle.** Once a statement
closes, every older transaction disappears from it and *no* parameter brings them back —
`start-date`/`from-date`/`statement-identifier` in both ISO and YYYYMMDD are all silently
ignored, and `moreRecordsIndicator` only means "more than this page". A pull on Sep 23 returned
45 rows covering Sep 18–23; the previous pull had 155 rows ending Sep 12. **Sep 13–17 existed in
neither.**

Two defences, both in `categorize.py`:

1. **`build_ledger()` unions every complete sync**, so a later narrow pull can never drop weeks
   an earlier one saw. Never categorise from a single file.
2. **Closed cycles come from the download CSV.** The UI's date-ranged endpoint is
   `…/digital-transaction-activity/v1/transaction-activities?account-activity-download-type-code=CSV
   &digital-account-identifier=…&start-date=YYYYMMDD&end-date=YYYYMMDD&csrftoken=…&submit=Submit
   &eligibility-indicator=true` — it 500s without `csrftoken`/`submit`/`eligibility-indicator`.
   Grab a live one from the Download Account Activity flow via network capture. Save to
   `raw/csv/` and `load_chase_csv()` picks it up. It has no MCC but does carry Chase's own
   Category column.

**CSVs fill only dates no JSON pull reached** — Chase's CSV description differs from the JSON
merchant name (`CITY HOSTEL` vs `City Hostel Stockholm AB`), so cross-source matching double-counts.

### Pending → Posted rewrites almost everything

Between pulls Chase changes the **date** *and* the **merchant name** for the same charge:
`SKYSS` → `SKYSS APP`, `BRITISH AIRWAYS US DIRECT ECOM` → `… US DUSA`, Agoda pending Sep 9 →
posted Sep 10. Exact-key dedup keeps both and every such charge is counted twice — it inflated
the trip by ~$330 before it was caught. The ledger reconciles on **amount + common merchant
prefix + date within 5 days**, dropping the pending twin. A fixed-length stem is not enough
(`SKYSS`/`SKYSSA` differ); compare how much of the two names actually agree.

Genuine same-day repeats (three Voi rides at $1.77) must survive — check that they still do
after touching this logic.

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

### Not only lodging spreads

`SPREAD` amortises **any** category across days — transit passes, museum cards, and aggregated
ride-hail bills. Bolt in particular charges as a *package*: `BOLT.EU/P/2609231506` carries an
embedded timestamp and covers a batch of rides, so a single charge on arrival day really belongs
to the whole stay and leaves the following days reading $0 transport.

```python
("BOLT.EU", 14.93, "2026-09-23", 4),   # Tallinn, Sep 23-26
```

A run of zero-transport days in a city you are clearly moving around is the signal to look for
a packaged charge rather than a missing one.

### Get the nights from the booking site, don't guess

Card data never carries stay dates — only a charge date. Open the OTA and read the reservation:

| Site | Where | Gives you |
|---|---|---|
| **Booking.com** | `secure.booking.com/mytrips.html` | dates + **guest count** ("2 adults" vs "1 adult") |
| **Hostelworld** | `hostelworld.com/account/trips/` — NOT `/mybookings`, which 404s | dates, incl. upcoming |

The guest count is the reliable signal for whether a stay is shared. Guessing from the merchant
name put a Helsinki hostel in the fjords and halved a charge that was entirely the user's.

**A stay often bills twice**: an OTA deposit on the booking date and the balance at check-in
(Hostelworld $14.66 on Sep 22 + Harbour Hub $82.95 on Sep 23). Both belong to the same stay and
must spread over the same nights.

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

`cdp-sync.mjs --write` does all of this itself — the guards included: it refuses to create
a block unless the previous block is `Week N-1` and `Metadata!B1` reads `N-1`. The shortcut
fires fine as a CDP key event (`Meta+Alt+Shift+1`), no menu clicking. The manual procedure,
for a Playwright browser:

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

Country cells validate against the `Countries` **named range** (`Metadata!B2:B60` since 11 Oct 2026)
with *reject input*, so a country missing from that list is silently refused and a
modal blocks every later keystroke. Denmark, Sweden, Norway, Finland, Estonia,
Latvia, Lithuania, Slovenia, Croatia, Italy, Netherlands, Germany, Poland, Czechia,
Austria, Slovakia, Hungary, Bosnia and Herzegovina, Montenegro, Albania and Serbia were
appended for this trip. The range now runs to row 60, so adding a country is just typing it
into the next empty `Metadata!B` cell. `categorize.py`'s `COUNTRY_NAME` must use the **same
spelling** ("Czechia", not "Czech Republic"); `cdp-sync.mjs` refuses to write a country the
list doesn't have. Never edit the validation rule itself — it just points at the name.

## Personal data lives outside the repo
`categorize.py` holds only rules and logic. The personal tables (merchant overrides, splits, cash entries, stays, the country timeline, holds) live in `~/Documents/sabbatical-finance/categorize_private.py`, or wherever `EXPENSE_PRIVATE` points. The script `exec`s that file into its globals at import time. Without it, the script runs with empty overrides and prints a note.
