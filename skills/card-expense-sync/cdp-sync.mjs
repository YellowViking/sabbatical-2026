#!/usr/bin/env node
// One-command card sync over the persistent CDP browser (../google-sheets-edit/cdp-up.sh).
//
//   node skills/card-expense-sync/cdp-sync.mjs                 # pull both banks, categorise, show weeks
//   node skills/card-expense-sync/cdp-sync.mjs --write         # ...and write those weeks to the sheet
//   node skills/card-expense-sync/cdp-sync.mjs --weeks 74-75   # choose the weeks (default: last 2 complete)
//   node skills/card-expense-sync/cdp-sync.mjs --no-pull       # re-categorise + write, no bank calls
//   node skills/card-expense-sync/cdp-sync.mjs --wait-login 30 # poll up to 30 min for sign-in, then go
//   ... --notify                                               # macOS notifications (for the weekly job)
//   ... --banks chase                                          # pull only these banks (default chase,amex)
//
// Exit 2 = a bank needs signing in; its tab is left open on the login page. With --wait-login
// the script instead keeps checking every 15 s, so the user only has to sign in.
//
// What it does, in order:
//   1. finds (or opens) the Chase and Amex tabs and checks each is signed in;
//   2. runs chase-pull.js / amex-pull.js INSIDE those tabs, in parallel, and writes the result
//      straight to raw/sync-<ts>.json — no sink server. (A bank page can no longer reach
//      127.0.0.1: Chrome 153's Local Network Access rules and Amex's CSP both block it.)
//   3. runs categorize.py, which unions every sync into the ledger;
//   4. prints the chosen weeks and warns about lodging with no STAYS rule;
//   5. with --write: creates any missing week block with the sheet's own "new week" macro,
//      types the numbers and countries, then reads the block back and diffs it.
//
// Everything financial stays under ~/Documents/sabbatical-finance — never in this public repo.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { attach, findTab, open } from '../google-sheets-edit/cdp.mjs';

const HERE = path.dirname(new URL(import.meta.url).pathname);
const FIN = path.join(os.homedir(), 'Documents/sabbatical-finance');
const CFG = JSON.parse(fs.readFileSync(path.join(FIN, 'accounts.json'), 'utf8'));
const CATS = ['Food&Drink', 'Lodging', 'Transportation', 'Other'];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const argv = process.argv.slice(2);
const flag = (f) => argv.includes(f);
const opt = (f) => (argv.includes(f) ? argv[argv.indexOf(f) + 1] : undefined);

// Sheet geometry. Blocks are 11 rows + 1 blank, so week N sits 12 rows per week below the
// first trip block. `firstWeek` is checked against the sheet's own label before any write.
const SHEET = { firstRow: 684, firstWeek: 69, startISO: '2026-08-23', ...CFG.sheet };
const SHEET_ID = SHEET.url.match(/\/d\/([^/]+)/)[1];
const blockRow = (n) => SHEET.firstRow + 12 * (n - SHEET.firstWeek);
const addDays = (iso, d) => new Date(Date.parse(iso) + d * 864e5).toISOString().slice(0, 10);
const weekStart = (n) => addDays(SHEET.startISO, 7 * (n - SHEET.firstWeek));

// ------------------------------------------------------------------------- 1-2. pull ----
const ALL_BANKS = [
  // `in` must POSITIVELY match a signed-in page. Spotting logged-out pages instead missed
  // Chase's marketing homepage ("Credit Card, Mortgage, Banking, Auto | Chase Online"), which
  // is where an expired session lands — the 20 Oct run then pulled straight into a 404.
  { name: 'chase', host: 'chase.com', url: 'https://secure.chase.com/web/auth/dashboard',
    in: /secure\.chase\.com\/web\/auth\/dashboard/, script: 'chase-pull.js' },
  { name: 'amex', host: 'americanexpress.com', url: 'https://global.americanexpress.com/activity/recent',
    in: /global\.americanexpress\.com\/(activity|dashboard|overview|summary)/, script: 'amex-pull.js' },
];
// Skipping a bank is safe: categorize.py unions every sync file, so a card left out this week
// is picked up — with its whole statement cycle — the next time it is pulled.
const BANKS = ALL_BANKS.filter((b) => (opt('--banks') ?? 'chase,amex').split(',').includes(b.name));
const LOGGED_OUT = /sign ?in|log ?[io]n|reauth|verify|logout|challenge/i;

// macOS notification, only with --notify (the weekly launchd job). Never put amounts from
// individual merchants here — notifications are visible on the lock screen.
function notify(msg) {
  if (!flag('--notify')) return;
  spawnSync('osascript', ['-e', `display notification ${JSON.stringify(msg)} with title "Expense tally"`]);
}

async function bankTab(b) {
  let sel = b.host;
  if (!(await findTab(b.host))) {
    // Attach by the new tab's id: right after opening, its URL can still be about:blank, so a
    // host match fails ("no tab matches", the 11 Oct weekly run).
    sel = await open(b.url);
    for (let i = 0; i < 30 && !(await findTab(b.host)); i++) await sleep(1000);
    await sleep(4000);
  }
  const tab = await attach(sel);
  const where = await tab.eval('() => ({ title: document.title, href: location.href })');
  if (!b.in.test(where.href) || LOGGED_OUT.test(where.title) || LOGGED_OUT.test(where.href)) {
    tab.close();
    return { needsLogin: `${b.name}: "${where.title}"` };
  }
  return { tab };
}

async function pullOne(b, tab) {
  const src = fs.readFileSync(path.join(HERE, b.script), 'utf8').replace(/^\/\/.*\n/gm, '');
  // A dead session often surfaces as a thrown "Failed to fetch" (the API redirects to a login
  // page on another origin) rather than a 401. Fold both into the same retry (18 Oct run).
  const run = () => tab.eval(src, JSON.stringify(CFG)).catch((e) => ({ error: e.message }));
  let out = await run();
  // A 401 straight after a browser restart is usually a cold session, not a logout: load the
  // bank's own page once, give it a few seconds, retry. (See SKILL.md "Warm the session".)
  if (out?.error && /40[134]|Failed to fetch/.test(out.error)) {
    await tab.nav(b.url); await sleep(8000);
    out = await run();
  }
  if (out?.error) {
    await tab.nav(b.url);                     // leave the tab on the bank's own sign-in screen
    throw Object.assign(new Error(`${b.name}: ${out.error} — session probably expired; sign in again`),
                        { session: true });
  }
  return out;
}

const WAIT_MIN = +(opt('--wait-login') ?? 0);
const DEADLINE = Date.now() + WAIT_MIN * 60e3;

async function signedIn() {
  const waitMin = WAIT_MIN; const deadline = DEADLINE;
  let said = '';
  for (;;) {
    const got = await Promise.all(BANKS.map(bankTab));
    const login = got.filter((g) => g.needsLogin).map((g) => g.needsLogin);
    if (!login.length) return got;
    got.forEach((g) => g.tab?.close());
    if (Date.now() >= deadline) {
      console.error(`sign in first — ${login.join('; ')}`);
      notify('Not run: sign-in timed out. Sign in to Chase and Amex, then run it again.');
      process.exit(2);
    }
    const who = login.map((l) => l.split(':')[0]).join(' + ');
    if (who !== said) {
      console.log(`waiting for sign-in: ${who} (up to ${waitMin} min)`);
      notify(`Sign in to ${who} in the debug Chrome — the tally runs as soon as you do.`);
      said = who;
    }
    await sleep(15000);
  }
}

async function pull() {
  // A session can look fine and still be dead: then the pull fails, and with --wait-login we go
  // back to waiting for a fresh sign-in instead of giving up.
  for (;;) {
    try { return await pullOnce(); } catch (e) {
      if (!e.session || Date.now() >= DEADLINE) throw e;
      console.log(`${e.message} — waiting again`);
      await sleep(15000);
    }
  }
}

async function pullOnce() {
  const got = await signedIn();
  try {
    const res = await Promise.all(BANKS.map((b, i) => pullOne(b, got[i].tab)));
    // Chase only: also save a rolling statement CSV. The JSON above is scoped to the CURRENT
    // statement cycle, so whenever a statement closes between two syncs (the 18th), the days
    // in between exist only here. The 20 Oct run got 19 rows and no trace of Oct 11-17.
    const ci = BANKS.findIndex((b) => b.name === 'chase');
    if (ci >= 0) {
      const ymd = (d) => d.toISOString().slice(0, 10).replace(/-/g, '');
      const end = new Date(); const start = new Date(Math.max(Date.parse(CFG.sinceISO), Date.now() - 75 * 864e5));
      const src = fs.readFileSync(path.join(HERE, 'chase-csv.js'), 'utf8').replace(/^\/\/.*\n/gm, '');
      const csv = await got[ci].tab.eval(src, JSON.stringify({ cfg: JSON.stringify(CFG), start: ymd(start), end: ymd(end) }));
      if (csv?.error) throw Object.assign(new Error(`chase csv: ${csv.error}`), { session: true });
      fs.mkdirSync(path.join(FIN, 'raw', 'csv'), { recursive: true });
      for (const [label, text] of Object.entries(csv)) {
        const f = `chase-${label.replace(/\W+/g, '')}-${ymd(start)}-${ymd(end)}.csv`;
        fs.writeFileSync(path.join(FIN, 'raw', 'csv', f), text);
        console.log(`csv       ${label} ${text.trim().split('\n').length - 1} rows -> raw/csv/${f}`);
      }
    }
    const by = Object.fromEntries(BANKS.map((b, i) => [b.name, res[i]]));
    const chase = by.chase ?? {}; const amex = by.amex ?? {};
    const counts = [
      ...Object.entries(chase).map(([k, v]) => `${k} ${v.length}`),
      ...Object.entries(amex).map(([k, v]) => `${k} ${v.transactions.length}`),
    ];
    if (!by.amex) counts.push('Amex skipped');
    const stamp = new Date().toISOString().replace(/[-:]/g, '').replace(/\.\d+/, '');
    const file = path.join(FIN, 'raw', `sync-${stamp}.json`);
    fs.writeFileSync(file, JSON.stringify({ pulledAt: new Date().toISOString(), chase, amex }));
    console.log(`pulled    ${counts.join(', ')} -> raw/${path.basename(file)}`);
  } finally { got.forEach((g) => g.tab?.close()); }
}

// -------------------------------------------------------------------- 3. categorise ----
function categorise() {
  const r = spawnSync('python3', [path.join(HERE, 'categorize.py')], { cwd: FIN, encoding: 'utf8' });
  if (r.status !== 0) throw new Error(`categorize.py failed:\n${r.stderr}`);
  for (const l of r.stdout.trim().split('\n')) if (/^(ledger|totals)/.test(l)) console.log(l);
}

const readCsv = (f) => {
  const [head, ...lines] = fs.readFileSync(path.join(FIN, f), 'utf8').trim().split(/\r?\n/);
  const cols = head.split(',');
  return lines.map((l) => {
    const cells = l.match(/("([^"]|"")*"|[^,]*)(,|$)/g).map((c) => c.replace(/,$/, '').replace(/^"|"$/g, ''));
    return Object.fromEntries(cols.map((c, i) => [c, cells[i]]));
  });
};

// ----------------------------------------------------------------------- 4. report ----
function weekRows(n, grid) {
  const days = Array.from({ length: 7 }, (_, i) => addDays(weekStart(n), i));
  return days.map((d) => grid.find((r) => r.date === d) ||
    { date: d, country: '', ...Object.fromEntries(CATS.map((c) => [c, '0.00'])) });
}

const LOOSE = [];
function report(weeks, grid) {
  for (const n of weeks) {
    const rows = weekRows(n, grid);
    console.log(`\nWeek ${n}  (${rows[0].date} .. ${rows[6].date})   row ${blockRow(n)}`);
    let tot = 0;
    for (const r of rows) {
      const day = CATS.reduce((s, c) => s + +r[c], 0); tot += day;
      console.log(`  ${r.date}  ${CATS.map((c) => (+r[c]).toFixed(2).padStart(8)).join(' ')}  ${day.toFixed(2).padStart(8)}  ${r.country}`);
    }
    console.log(`  ${'week total'.padEnd(46)}${tot.toFixed(2).padStart(9)}   ($${(tot / 7).toFixed(2)}/day)`);
  }
  // Lodging that was charged but never spread is almost always a missing STAYS rule.
  const lo = weekStart(weeks[0]); const hi = addDays(weekStart(weeks.at(-1)), 6);
  const loose = readCsv('transactions-classified.csv')
    .filter((t) => t.date >= lo && t.date <= hi && /NOT amortised/.test(t.note || '') && t.card !== 'cash');
  for (const t of loose) console.log(`  ⚠ no STAYS rule: ${t.date} ${t.merchant} ${t.amount}`);
  LOOSE.push(...loose);
}

// ------------------------------------------------------------------------ 5. write ----
const money = (s) => +String(s).replace(/[$,]/g, '') || 0;

async function sheetTab() {
  if (!(await findTab(`spreadsheets/d/${SHEET_ID}`))) { await open(SHEET.url); await sleep(12000); }
  return attach(`spreadsheets/d/${SHEET_ID}`);
}

const gviz = (tab, sheet, range) => tab.eval(`async () => {
  const r = await fetch('/spreadsheets/d/${SHEET_ID}/gviz/tq?tqx=out:csv&headers=0&sheet=${sheet}&range=${range}',
                        { credentials: 'include' });
  return (await r.text()).trim().split('\\n').map(l => [...l.matchAll(/"([^"]*)"/g)].map(m => m[1]));
}`);

async function ensureBlock(tab, n) {
  const row = blockRow(n);
  const label = await tab.cell(`Weeks!A${row}`);
  if (label === `Week ${n}`) return;
  if (label) throw new Error(`Weeks!A${row} reads "${label}", expected "Week ${n}" — geometry is off`);
  // Missing: only create it directly after the previous block, and only if the macro's
  // counter agrees, or the macro would stamp a colliding week number.
  const prev = await tab.cell(`Weeks!A${row - 12}`);
  const counter = await tab.cell('Metadata!B1');
  if (prev !== `Week ${n - 1}` || counter !== String(n - 1)) {
    throw new Error(`cannot create Week ${n}: A${row - 12}="${prev}", Metadata!B1="${counter}"`);
  }
  // Fire the macro ONCE and then keep hands off the grid until Apps Script reports done.
  // The macro pastes at whatever is selected *when it executes*, and Apps Script can sit on
  // "Running script" for minutes. On 20 Oct a slow run finished late, a cancel didn't take,
  // and two retries each bumped CurrentWeek (75 -> 78) — so: no re-fire, no cell reads (they
  // move the selection) while it runs, and the label is checked via gviz, which selects nothing.
  const banner = () => tab.eval(`() => [...document.querySelectorAll('[role=alert]')]
    .some((e) => /Running script/.test(e.innerText))`);
  if (await banner()) throw new Error('a script is already running in the sheet — wait and retry');
  await tab.cell(`Weeks!A${row}`);
  await tab.key('Meta+Alt+Shift+1');                    // Extensions > Macros > "new week"
  let seen = false;
  for (let i = 0; i < 120; i++) {                       // up to ~4 min
    await sleep(2000);
    const running = await banner(); seen ||= running;
    if (seen && !running) break;
    if (!seen && i >= 10) break;                        // never started (20 s)
  }
  const stamped = (await gviz(tab, 'Weeks', `A${row}:A${row}`))[0]?.[0];
  if (stamped !== `Week ${n}`) {
    throw new Error(`macro did not stamp Week ${n} at A${row} (got "${stamped ?? ''}", started=${seen}). ` +
      'Not retrying: check the sheet and Metadata!B1 by hand first.');
  }
  // The macro stamps the label before it bumps the counter, so give B1 a few seconds (1 Nov:
  // read too early, it said 77 a moment before turning 78).
  let after = '';
  for (let i = 0; i < 8 && (after = await tab.cell('Metadata!B1')) !== String(n); i++) await sleep(2000);
  if (after !== String(n)) throw new Error(`Week ${n} created but Metadata!B1 = ${after} — fix the counter`);
  console.log(`  created Week ${n} with the macro at row ${row}`);
}

async function writeWeek(tab, n, grid, allowed) {
  const row = blockRow(n); const d0 = row + 2; const d6 = row + 8;
  const rows = weekRows(n, grid);
  const bad = rows.map((r) => r.country).filter((c) => c && !allowed.has(c));
  // A country outside the `Countries` named range pops a modal that eats every later keystroke.
  if (bad.length) throw new Error(`add to Metadata Countries first: ${[...new Set(bad)].join(', ')}`);

  await ensureBlock(tab, n);
  // Numbers: ONE clipboard paste of the 7x4 grid. Typing ~200 keystrokes broke on 25 Oct when
  // another agent was driving the same Chrome — focus moved and values landed in wrong cells.
  // A paste can silently not land (1 Nov: the first attempt left the block at $0.00 while the
  // retry worked), so read the numbers back and re-paste up to 3 times before giving up.
  const tsv = rows.map((r) => CATS.map((c) => (+r[c]).toFixed(2)).join('\t')).join('\n');
  for (let attempt = 1; attempt <= 3; attempt++) {
    await tab.cell(`Weeks!B${d0}:E${d6}`);
    await tab.paste(tsv);
    await sleep(2000);
    const back = await gviz(tab, 'Weeks', `A${d0}:E${d6}`);
    const ok = rows.every((r, i) => { const l = back.find((g) => g[0] === String(i + 1));
      return l && CATS.every((c, j) => Math.abs(money(l[j + 1]) - +r[c]) <= 0.005); });
    if (ok) break;
    console.log(`  paste attempt ${attempt} did not land — retrying`);
  }
  // Countries are dropdowns, which a paste would wipe, so they are typed — one cell at a time,
  // each with its own selection, and only where the sheet differs.
  if (rows.every((r) => r.country)) {
    const now = await gviz(tab, 'Weeks', `A${d0}:G${d6}`);
    for (const [i, r] of rows.entries()) {
      if (now.find((g) => g[0] === String(i + 1))?.[6] === r.country) continue;
      await tab.cell(`Weeks!G${d0 + i}`);
      await tab.type(r.country + '\n');
    }
  }
  await sleep(1500);

  // Read back by DAY NUMBER, not position — gviz drops rows, so positions can't be trusted.
  const got = await gviz(tab, 'Weeks', `A${d0}:G${d6}`);
  const diffs = [];
  rows.forEach((r, i) => {
    const line = got.find((g) => g[0] === String(i + 1));
    if (!line) return diffs.push(`day ${i + 1} missing from read-back`);
    CATS.forEach((c, j) => {
      if (Math.abs(money(line[j + 1]) - +r[c]) > 0.005) diffs.push(`${r.date} ${c}: sheet ${line[j + 1]} want ${r[c]}`);
    });
    if (r.country && line[6] !== r.country) diffs.push(`${r.date} country: sheet ${line[6]} want ${r.country}`);
  });
  // The day rows can be right while the block around them is broken: on 25 Oct a botched typing
  // run overwrote the Transportation SUM, the "Grand Total:" label and the blank separator rows,
  // and the day-row check still passed. So also check the grand total and both separators.
  const want = rows.reduce((s, r) => s + CATS.reduce((t, c) => t + +r[c], 0), 0);
  const grand = money((await gviz(tab, 'Weeks', `E${row + 10}:E${row + 10}`))[0]?.[0]);
  if (Math.abs(grand - want) > 0.01) diffs.push(`grand total E${row + 10}: sheet ${grand.toFixed(2)} want ${want.toFixed(2)}`);
  for (const sep of [row - 1, row + 11]) for (const c of ['A', 'B', 'C', 'D', 'E', 'F', 'G']) {
    const v = await tab.cell(`Weeks!${c}${sep}`);
    if (v && sep === row + 11 && /^Week \d+$/.test(v)) continue;   // next block's label is fine
    if (v) diffs.push(`separator ${c}${sep} should be empty, has "${v}"`);
  }
  console.log(diffs.length ? `  ✗ Week ${n}:\n    ${diffs.join('\n    ')}` : `  ✓ Week ${n} verified (days, grand total, separators)`);
  return !diffs.length;
}

// -------------------------------------------------------------------------- main ----
function defaultWeeks() {
  // The last two COMPLETE weeks: the most recent, plus the one before it to catch late posts.
  // LOCAL date, not UTC: at 00:35 CET on a Sunday it is still Saturday in UTC, which made the
  // 8 Nov run think Week 79 wasn't finished and rewrite 77-78 instead of 78-79.
  const today = new Date(Date.now() - new Date().getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
  const done = Math.floor((Date.parse(today) - Date.parse(SHEET.startISO)) / (7 * 864e5)) - 1;
  return [SHEET.firstWeek + done - 1, SHEET.firstWeek + done];
}

const weeks = opt('--weeks')
  ? (([a, b]) => Array.from({ length: (b ?? a) - a + 1 }, (_, i) => a + i))(opt('--weeks').split('-').map(Number))
  : defaultWeeks();

try {
  if (!flag('--no-pull')) await pull();
  categorise();
  const grid = readCsv('sheet-rows.csv');
  report(weeks, grid);

  if (flag('--write')) {
    console.log('\nwriting');
    const tab = await sheetTab();
    try {
      const first = await tab.cell(`Weeks!A${SHEET.firstRow}`);
      if (first !== `Week ${SHEET.firstWeek}`) throw new Error(`Weeks!A${SHEET.firstRow} is "${first}", not "Week ${SHEET.firstWeek}"`);
      const allowed = new Set((await gviz(tab, 'Metadata', 'B2:B60')).map((r) => r[0]).filter(Boolean));
      let ok = true;
      for (const n of weeks) ok = (await writeWeek(tab, n, grid, allowed)) && ok;
      process.exitCode = ok ? 0 : 1;
      const last = weekRows(weeks.at(-1), grid).reduce((s, r) => s + CATS.reduce((t, c) => t + +r[c], 0), 0);
      notify(ok ? `Week ${weeks.at(-1)} on the sheet: $${last.toFixed(2)}${LOOSE.length ? ` · ${LOOSE.length} lodging charge(s) need a STAYS rule` : ''}`
                : 'Written, but the read-back did not match — see the log.');
    } finally { tab.close(); }
  }
} catch (e) {
  console.error(e.message);
  notify(`Failed: ${e.message.slice(0, 120)}`);
  process.exitCode = 1;
}
