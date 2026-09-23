/**
 * Google Maps personal labels — batch helper
 *
 * Creates private "Add a label" labels on COORDINATE / address pins
 * (i.e. places with NO business listing). UI-driven; no internal API.
 *
 * Usage (Playwright):
 *   node batch-label.js targets.json        // standalone
 *   — or paste the `run(playwrightPage, targets)` body into
 *     Playwright MCP `browser_run_code_unsafe` (it receives `page`).
 *
 * targets.json:
 *   [
 *     { "lat": 56.9526118, "lng": 24.1236183, "label": "City Nest (Kr. Barona 21a)" },
 *     { "lat": 56.9492893, "lng": 24.1199034, "label": "M6 Rooms (Merkela 6)" }
 *   ]
 *
 * IMPORTANT
 *  - Only works on coordinate pins. Business listings have NO "Add a label"
 *    button — they are already findable by name (use google-maps-saved-places).
 *  - Labels are NOT searchable by name — retrieve via address or coordinates.
 */

/** Core loop. `page` = Playwright Page from an authenticated session. */
async function run(page, targets) {
  const results = [];
  for (const t of targets) {
    try {
      await page.goto(
        `https://www.google.com/maps/place/${t.lat},${t.lng}/@${t.lat},${t.lng},17z?hl=en`
      );
      await page.waitForTimeout(3500); // map + card settle

      const addBtn = page.getByRole('button', { name: 'Add a label' });
      await addBtn.waitFor({ timeout: 8000 }); // fails on business listings
      await addBtn.click();
      await page.waitForTimeout(1200);

      const combo = page.getByRole('combobox', { name: 'Add a label' });
      await combo.waitFor({ timeout: 5000 });
      await combo.fill(t.label);
      await page.waitForTimeout(400);
      await combo.press('Enter');
      await page.waitForTimeout(1800);

      const body = await page.locator('body').innerText();
      const m = body.match(/Created label [^\n.]*/);
      results.push({ label: t.label, ok: !!m, status: m ? m[0] : 'NO CONFIRM' });
    } catch (e) {
      results.push({
        label: t.label,
        ok: false,
        status: 'ERR ' + e.message.slice(0, 120),
        // hint: likely a business listing (no label action) or not signed in
      });
    }
  }
  return results;
}

/** Verify a label stuck: re-open the same coordinate and read the card h1. */
async function verify(page, targets) {
  const out = [];
  for (const t of targets) {
    await page.goto(
      `https://www.google.com/maps/place/${t.lat},${t.lng}/@${t.lat},${t.lng},17z?hl=en`
    );
    await page.waitForTimeout(3000);
    const h1s = await page.locator('h1').allInnerTexts().catch(() => []);
    out.push({
      expect: t.label,
      got: h1s.filter(Boolean)[0] || null,
      ok: (h1s.filter(Boolean)[0] || '') === t.label,
    });
  }
  return out;
}

/**
 * Classify a property: does it have a named Maps listing (skip) or is it
 * address-only (label it)? Search the name and inspect the h1.
 */
async function classify(page, name) {
  await page.goto(
    'https://www.google.com/maps/search/' + encodeURIComponent(name) + '?hl=en'
  );
  await page.waitForTimeout(3000);
  const h1 = (await page.locator('h1').first().innerText().catch(() => '')) || '';
  // "Results" / empty => no listing (address-only) => LABEL IT
  // otherwise => direct listing => NO LABEL NEEDED
  const hasListing = h1 && h1 !== 'Results' && !/^\s*$/.test(h1);
  return { name, h1, hasListing };
}

module.exports = { run, verify, classify };

// Standalone runner (optional): node batch-label.js targets.json
if (require.main === module) {
  (async () => {
    const { chromium } = require('playwright');
    const fs = require('fs');
    const targets = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
    const browser = await chromium.launch({ channel: 'chrome' });
    const ctx = await browser.newContext(); // reuse a logged-in profile in practice
    const page = await ctx.newPage();
    const res = await run(page, targets);
    console.log(JSON.stringify(res, null, 1));
    console.log(JSON.stringify(await verify(page, targets), null, 1));
    await browser.close();
  })();
}
