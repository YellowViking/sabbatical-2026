// Write a block of cells into an open Google Sheet by pasting TSV.
//
//   browser_run_code_unsafe { filename: ".../google-sheets-edit/paste.js" }
//
// Reads its job from http://127.0.0.1:8899/payload (see sink.py) so large grids never have to be
// inlined into a prompt. Payload shape:
//   { "url": "https://docs.google.com/spreadsheets/d/<ID>/edit#gid=0",   // optional
//     "writes": [ { "anchor": "A684", "tsv": "…\t…\n…", "mode": "values" }, … ],
//     "verify":  ["A684", "E694", …] }                                    // optional read-back
//
// mode "values" pastes values only (Cmd/Ctrl+Shift+V). Use it when writing INTO an existing
// formatted block: a normal paste replaces the target's number formats AND its data validation,
// which silently destroys dropdowns. mode defaults to "normal" (whole-cell paste).
//
// Why paste and not the Sheets API: this drives the already-signed-in browser, so it needs no
// OAuth client, no service account and no sharing changes. Tabs, newlines and leading `=` are
// interpreted by Sheets exactly as if a human pasted, so formulas land as formulas.
//
// Gotchas this encodes:
//  * Selecting via the name box (#t-name-box) is the only reliable way to land on a far-off cell.
//  * grantPermissions(['clipboard-read','clipboard-write']) is required before navigator.clipboard.
//  * A real keyboard Meta+V (Ctrl+V off macOS) is required — a synthetic paste event is ignored.
//  * Sheets needs a beat after each paste; without the waits the next selection races the render.

async (page) => {
  const SINK = 'http://127.0.0.1:8899';
  const job = await (await page.context().request.get(`${SINK}/payload`)).json();

  if (job.url && !page.url().startsWith(job.url.split('#')[0])) {
    await page.goto(job.url);
    await page.waitForTimeout(3000);
  }

  await page.context().grantPermissions(['clipboard-read', 'clipboard-write'], {
    origin: 'https://docs.google.com',
  });

  const isMac = await page.evaluate(() => navigator.platform.toUpperCase().includes('MAC'));
  const MOD = isMac ? 'Meta' : 'Control';
  const KEY = { normal: `${MOD}+V`, values: `${MOD}+Shift+V` };

  const select = async (a1) => {
    await page.evaluate((a) => {
      const nb = document.querySelector('#t-name-box');
      nb.focus();
      nb.select();
      document.execCommand('insertText', false, a);
      nb.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
    }, a1);
    await page.waitForTimeout(700);
  };

  const readCell = async (a1) => {
    await select(a1);
    return page.evaluate(() =>
      document.querySelector('#t-formula-bar-input').innerText.replace(/\n$/, '')
    );
  };

  const done = [];
  for (const w of job.writes || []) {
    await page.evaluate((t) => navigator.clipboard.writeText(t), w.tsv);
    await select(w.anchor);
    await page.keyboard.press(KEY[w.mode || 'normal']);
    await page.waitForTimeout(1500);
    done.push(`${w.anchor}:${w.mode || 'normal'}`);
  }

  // Restore number formats that a normal paste flattened, by copying a formatted source range.
  if (job.formatFrom) {
    await select(job.formatFrom);
    await page.keyboard.press(`${MOD}+C`);
    await page.waitForTimeout(900);
    for (const target of job.formatTo || []) {
      await select(target);
      await page.keyboard.press(`${MOD}+Alt+V`); // paste format only
      await page.waitForTimeout(1200);
    }
    await page.keyboard.press('Escape');
  }

  // Cells under data validation (dropdowns) must be TYPED, not pasted: any paste replaces the
  // validation rule along with the value and the dropdown silently disappears.
  for (const t of job.types || []) {
    await select(t.cell);
    await page.keyboard.type(t.text);
    await page.keyboard.press('Enter');
    await page.waitForTimeout(450);
    done.push(`${t.cell}:typed`);
  }

  const verified = {};
  for (const a1 of job.verify || []) verified[a1] = await readCell(a1);

  return JSON.stringify({ pasted: done, verified }, null, 1);
}
