---
name: google-sheets-edit
description: >
  Read and write a Google Sheet from an already-signed-in Playwright/Chrome
  session, with no OAuth client, service account or sharing change. Reads via the
  gviz CSV endpoint, writes by pasting TSV (formulas included) at a named anchor,
  and copies number formatting from an existing range. Use whenever a task needs
  to update a spreadsheet the user owns, e.g. the sabbatical expense sheet.
---

# Editing a Google Sheet from a logged-in browser

## Why this way

The Sheets API v4 needs an OAuth client or a service account plus a sharing
change. If a browser is already signed in as the owner, everything below works
with zero credential setup — reads are one `fetch`, writes are a clipboard paste
that Sheets parses exactly as if a human had pasted.

## Reading

```js
const id = '<SPREADSHEET_ID>';
const url = `https://docs.google.com/spreadsheets/d/${id}/gviz/tq`
          + `?tqx=out:csv&headers=0&sheet=Weeks&range=A594:H645`;
const csv = await (await fetch(url, {credentials:'include'})).text();
```

- Must run **inside a `docs.google.com` tab** (`page.evaluate`). Same-origin;
  `/export?format=csv` cross-redirects and fails CORS.
- `sheet=<TabName>` selects the tab without needing its `gid`. Tab names are also
  readable from the DOM: `document.querySelectorAll('.docs-sheet-tab')`.
- `headers=0` stops gviz consuming the first row as a header.

### Two gviz traps that will bite you

1. **Row numbers are not trustworthy.** gviz drops rows (blank ones, and others
   unpredictably). An unranged export of a 679-row sheet came back 2 rows short by
   the end, so every computed row number was wrong. Passing `&range=` narrows the
   damage but does **not** eliminate it. **Any time exact row numbers matter,
   confirm them in the formula bar** (below), not from gviz.
2. **Text in a numeric column is silently dropped.** gviz types each column; a
   string header sitting in an otherwise-numeric column returns `""`. That is why
   header rows look half-empty in the CSV.

### Ground truth: the name box + formula bar

Slow (~0.6 s/cell) but exact, and the only way to see *formulas* rather than
values:

```js
const nb = document.querySelector('#t-name-box');
nb.focus(); nb.select();
document.execCommand('insertText', false, 'B686');
nb.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', keyCode:13, bubbles:true}));
await new Promise(r => setTimeout(r, 650));
document.querySelector('#t-formula-bar-input').innerText;   // "=SUM(B686:E686)"
```

Use it to map a template block, to find the true last used row, and to verify
after writing.

## Writing — `paste.js`

```
browser_run_code_unsafe { filename: "skills/google-sheets-edit/paste.js" }
```

It reads its job from `http://127.0.0.1:8899/payload` (see
`../card-expense-sync/sink.py`), so a large grid never has to be inlined in a
prompt:

```json
{ "url": "https://docs.google.com/spreadsheets/d/<ID>/edit?gid=0#gid=0",
  "writes": [ { "anchor": "A684", "tsv": "Week 69\tCurrency:\tUSD\t=VLOOKUP(C684,pairs,2,FALSE)\n…" } ],
  "verify": ["A684", "B686", "E694"] }
```

Tabs are columns, newlines are rows, a leading `=` becomes a real formula, and
relative references are **not** rewritten — write them already resolved for the
destination rows.

### What makes the paste work

- `context.grantPermissions(['clipboard-read','clipboard-write'], {origin:'https://docs.google.com'})`
  before touching `navigator.clipboard`. (`writeText` then succeeds even though
  `readText` may still return `""` — that is fine, only the write matters.)
- Select the anchor **through the name box**; scrolling/clicking to a far-off row
  is unreliable.
- Press a **real** `Meta+V` (`Control+V` off macOS) via `page.keyboard`. A
  synthetic `paste` event with `clipboardData` is ignored by Sheets.
- Wait ~1.5 s after each paste; without it the next selection races the render.

### Cells with dropdowns must be typed, not pasted

Any paste replaces the target's **data validation** along with its value, so
pasting into a dropdown column silently destroys the dropdown. `Cmd+Shift+V`
(paste values only) does *not* help — Sheets ignores it for system-clipboard
content; the cells simply stay unchanged.

So write those cells with `types` instead, one at a time:

```json
"types": [ { "cell": "G686", "text": "Denmark" } ]
```

And beware the failure mode: if the value is not in the validation list and the
rule is *reject input*, Sheets throws a modal —

> There was a problem — The data you entered in cell G686 violates the data
> validation rules set on this cell.

which then **swallows every subsequent keystroke**, so later unrelated edits
vanish with no error. If a run's writes mysteriously do nothing, screenshot
before assuming the selector was wrong. Fix the list first (below), don't retry.

### Check whether a rule points at a named range

Select a cell, **Data > Data validation**, click the rule. If the criteria shows
`=SomeName`, do not edit the rule — widen the name under **Data > Named ranges**.
That fixes every block at once, including future ones. Named ranges in this
sheet: `Countries`, `CurrentWeek`, `pairs`, `WeeklyTemplate`.

### Prefer the sheet's own macro

If the workbook has a bound macro that builds the structure you are about to
build (Extensions > Macros), use it. It carries formatting, dropdowns and
bookkeeping counters that a TSV paste cannot. Read its source at
**Extensions > Apps Script** first — the Monaco model is readable with
`monaco.editor.getModels().map(m => m.getValue())`.

### Formatting

A paste into never-formatted cells carries values but not number formats, so new
cells show `52.38` where the rest of the sheet shows `$52.38`. Copy the format
from an existing block:

```js
await select('A672:G682');  await page.keyboard.press('Meta+C');
await select('A684:G694');  await page.keyboard.press('Meta+Alt+V');  // paste format only
```

`Meta+Alt+V` is paste-format-only on macOS (`Control+Alt+V` elsewhere). It brings
no values, so it is safe to apply over freshly written data.

## When the Playwright browser is locked by another agent

`Browser is already in use for …/ms-playwright-mcp/mcp-chrome-<id>` means the MCP server lost
its attachment and cannot relaunch because the old Chrome still holds the profile lock. Every
Playwright tool then fails. **Do not kill that Chrome** — another agent may be using it, and it
holds live logins.

Escape hatch: a *separate*, **persistent** Chrome on a CDP port, driven with the
`chrome-devtools-cdp` MCP (which expects `127.0.0.1:9222`).

```bash
bash skills/google-sheets-edit/cdp-up.sh     # idempotent; reuses a running instance
```

**Never kill it, and never delete its profile.** It lives at
`~/Documents/sabbatical-finance/chrome-cdp-profile` and keeps its Google session between runs,
so nobody has to sign in again. Tearing it down each time is the mistake — it only creates
re-login work. (The profile holds live Google cookies, which is why it sits outside the public
repo and outside `/tmp`.)

On first run the script seeds the cookie jar from the Playwright profile, which **does** carry
the Google session. Two traps it handles:
- Cookies are at `Default/Cookies`, **not** `Default/Network/Cookies`.
- There are usually several stale `mcp-chrome-*` profiles; seed from the one with the **largest
  cookie jar**, not the first alphabetically, or you land on a sign-in page.

First load may bounce through a sign-in redirect and resolve itself — wait ~10 s and re-list
pages before concluding it failed.

Then `list_pages` → `evaluate_script` for name-box selection, `press_key` for `Delete`,
`type_text` for cell entry.

**Clipboard paste does NOT work over this CDP bridge.** `press_key "Meta+V"` reports success and
does nothing — Sheets never sees a trusted paste, even though `navigator.clipboard.writeText`
succeeds and `readText` reads it back. Playwright's `keyboard.press` does work; the CDP tool's
does not. Use `type_text` instead:

- **Newlines reliably move down one cell.** Type a whole column in one call.
- **Tabs are NOT reliable — do not type a TSV block.** Sometimes they move right, sometimes the
  literal tab characters land in the cell, leaving `37.78 71.81 16.19 29.25` as a text string in
  the first column while the other columns keep their old values. The day-total formulas then
  read 0 and the corruption looks like a formatting glitch. **Write column by column**: select
  `B<top>`, type the B values newline-separated, then `C<top>`, and so on.
- Typing preserves the target's number format and data validation, so it is also the right way
  to fill dropdown columns.

When re-writing a block that already exists, **diff first and type only the changed cells** —
usually a handful. A full re-paste is rarely needed.

⚠️ **Verify on a cell whose value actually changed.** Checking `B686` after a re-write proved
nothing, because that figure was identical in the old and new data — three "successful" pastes
were silently no-ops. Pick a cell you know differs, or screenshot.

**Leave the browser running when done.** It costs nothing idle and saves a sign-in next time.

## Verifying

`paste.js` takes a `verify` list and returns each cell's formula-bar contents.
Check an anchor, a data cell, a country cell and a grand total per block. A
screenshot is worth taking too — it catches formatting and merged-cell surprises
that a cell-by-cell read will not.
