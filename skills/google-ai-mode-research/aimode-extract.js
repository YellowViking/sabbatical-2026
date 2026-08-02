/**
 * Google AI Mode fast extract helpers (personal logged-in session).
 * Use from Playwright page.evaluate / agent browser_run_code.
 *
 * No stable public generate API — navigate udm=50 and early-stop on DOM text.
 */

function buildAimodeUrl(query, { hl = 'en' } = {}) {
  const u = new URL('https://www.google.com/search');
  u.searchParams.set('udm', '50');
  u.searchParams.set('hl', hl);
  u.searchParams.set('q', query);
  return u.toString();
}

/** Call in page context */
function extractAimodeText() {
  const t = (document.querySelector('main') || document.body).innerText || '';
  const i = t.indexOf('AI Mode Conversation');
  return i >= 0 ? t.slice(i) : t;
}

/** Call in page context — usefulness heuristic for early-stop */
function aimodeUseful(minLen = 1800) {
  const body = extractAimodeText();
  const ready = /AI Mode response is ready/i.test(
    (document.querySelector('main') || document.body).innerText || ''
  );
  const hasStars = /4\.[0-9]/.test(body);
  const hasMoney = /(?:NOK|SEK|DKK|USD|€|\$)\s*\d|\d+\s*(?:NOK|SEK|DKK|USD)/i.test(body);
  const hasOrder = /Must-Order|Google Rating|order this|~\d+/i.test(body);
  const tableish = ((body.match(/\t/g) || []).length > 5) || hasOrder;
  return {
    ready,
    len: body.length,
    useful: ready || (body.length >= minLen && hasStars && (hasMoney || tableish)),
    hasStars,
    hasMoney,
  };
}

/**
 * Playwright-side driver (pass `page` from MCP/run_code).
 * Ensures Pro once if menu available, navigates, early-stops, returns text.
 */
async function aimodeQuery(page, query, opts = {}) {
  const {
    ensurePro = true,
    minLen = 1800,
    pollMs = 400,
    maxWaitMs = 45000,
    hl = 'en',
  } = opts;

  if (ensurePro) {
    try {
      const open = page.getByRole('button', { name: /Add files, tools, and select/i });
      if (await open.count()) {
        await open.first().click();
        await page.waitForTimeout(500);
        const pro = page.getByRole('menuitemradio', { name: /^Pro$/i });
        if (await pro.count()) {
          const checked = await pro.first().getAttribute('aria-checked');
          if (checked !== 'true') await pro.first().click({ force: true });
        }
        await page.keyboard.press('Escape').catch(() => {});
      }
    } catch {
      /* menu not on page yet — open URL first then retry once below */
    }
  }

  const url = buildAimodeUrl(query, { hl });
  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'commit', timeout: 60000 });

  if (ensurePro) {
    try {
      const open = page.getByRole('button', { name: /Add files, tools, and select/i });
      // wait briefly for chrome
      for (let i = 0; i < 10 && !(await open.count()); i++) await page.waitForTimeout(300);
      if (await open.count()) {
        await open.first().click();
        await page.waitForTimeout(400);
        const pro = page.getByRole('menuitemradio', { name: /^Pro$/i });
        if (await pro.count()) {
          const checked = await pro.first().getAttribute('aria-checked');
          if (checked !== 'true') await pro.first().click({ force: true });
        }
        await page.keyboard.press('Escape').catch(() => {});
        // model switch may restart generation — continue polling
      }
    } catch {
      /* ignore */
    }
  }

  let last = '';
  while (Date.now() - t0 < maxWaitMs) {
    await page.waitForTimeout(pollMs);
    const st = await page.evaluate(
      ({ minLen }) => {
        const t = (document.querySelector('main') || document.body).innerText || '';
        const i = t.indexOf('AI Mode Conversation');
        const body = i >= 0 ? t.slice(i) : t;
        const ready = /AI Mode response is ready/i.test(t);
        const hasStars = /4\.[0-9]/.test(body);
        const hasMoney = /(?:NOK|SEK|DKK|USD|€|\$)\s*\d|\d+\s*(?:NOK|SEK|DKK|USD)/i.test(body);
        const hasOrder = /Must-Order|Google Rating|order this/i.test(body);
        const tableish = ((body.match(/\t/g) || []).length > 5) || hasOrder;
        return {
          body,
          ready,
          useful: ready || (body.length >= minLen && hasStars && (hasMoney || tableish)),
          len: body.length,
        };
      },
      { minLen }
    );
    if (st.body && st.body.length >= last.length) last = st.body;
    if (st.useful) {
      return {
        ok: true,
        ms: Date.now() - t0,
        ready: st.ready,
        text: last,
        url: page.url(),
      };
    }
  }

  return {
    ok: false,
    ms: Date.now() - t0,
    ready: false,
    text: last,
    url: page.url(),
    error: 'timeout waiting for useful AI Mode answer',
  };
}

module.exports = {
  buildAimodeUrl,
  extractAimodeText,
  aimodeUseful,
  aimodeQuery,
};
