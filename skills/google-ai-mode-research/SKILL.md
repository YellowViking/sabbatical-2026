---
name: google-ai-mode-research
description: >
  Fast Google AI Mode (udm=50) research from a logged-in Playwright Chrome
  session. Prefer Pro model when available. Extract answer text via DOM early-
  stop — there is no stable public StreamGenerate body API for Search AI Mode.
  Use for multi-city food/sights research on the sabbatical trip.
---

# Google AI Mode research (fast path)

## Sign-in + Pro model

Playwright MCP (`@playwright/mcp --browser chrome`) already shows:

```
Google Account: Buyu Chen (destiny.fox.1990@gmail.com)
```

**You do not need to paste passwords into chat.** If Sign in appears:

1. Open AI Mode in the Playwright-controlled Chrome window.
2. Click **Sign in** / account chip and finish Google login + 2SV **yourself** in that window.
3. Confirm avatar shows your name/email (not “Sign in”).

### Switch to Pro (each new browser profile / cold start)

1. Open any `https://www.google.com/search?udm=50&q=...`
2. Click **“Add files, tools, and select a model”**
3. Under **Gemini 3 models**, select **Pro** (not Fast)
4. If Pro is greyed / weak quality, header **Upgrade** → Google One AI  
   `https://one.google.com/ai?...` may be required for full Pro

UI labels (Jul 2026): menuitemradio `Fast` | `Pro`.

Sticky for the session after click; re-check after browser restart.

---

## Direct API — what we proved (live, signed-in, Jul 2026)

**Short answer:** there is a backend call that carries the answer (`GET /async/folwr`), but it is **not** a stable, mintable “direct API” like Maps `createitem`. You cannot reliably curl it without the full AI Mode JS client.

### Where the answer actually lives

| Call | Carries answer? | Notes |
|---|---|---|
| `GET /search?udm=50&q=` | **No** (shell only) | ~410KB HTML in ~0.3s; has seeds/tokens; **no** restaurant body |
| `GET /async/folwr?srtst&garc&mlro&…` | **Yes** | ~400–530KB HTML fragment; `data-container-id`, answer text inside |
| `AimThreadsService/ListThreads` | No | Sidebar history |
| `async/hpba`, `async/bgasy` | No | Progressive chrome / BotGuard |
| `wizrpcui/.../batchexecute` | No | Tiny UI RPC |
| Gemini `StreamGenerate` / AI Studio API | **Not used** by Search AI Mode in this capture | Zero hits |

### Token seeds **are** in first HTML

On the shell page (no full render), attributes exist:

- `data-garc`
- `data-lro-token` + `data-lro-signature`
- `data-xsrf-folwr-token` / `folwr-token` (`srtst`)
- `data-stkp`
- `kEI` / `opi`

### Replay / mint experiments (failed)

| Experiment | Result |
|---|---|
| Re-`fetch` a **live** folwr URL that just returned 200 + answer | **404** (one-shot / bound to page load) |
| Build folwr from shell tokens (`srtst+garc+mlro+mlros+ei+q+stkp+xsrf`) | **400** every time |
| Poll that minted URL for ~6s | still **400** |
| POST form body to `/async/folwr` | **404** |
| Same-origin `fetch(/search?udm=50)` alone | HTML shell only; answer never present |

So something in the **bundled AI Mode JS** (likely mlro evolution, `vet`/`ved`, BotGuard, or a missing header) is required before folwr accepts the request. That is **not** the same class of problem as Maps `createitem` (mutate one harvested URL). Worth revisiting only if we decompile `search-next.aim` and fully emulate the client — high churn, low payoff vs DOM early-stop.

### Practical API surface for agents

```
navigate udm=50 → (browser runs real client) → poll main.innerText → early-stop
```

Optional future: intercept the **first successful folwr response body** via Playwright `page.on('response')` and parse HTML there (skip waiting for full React paint). Still needs a real navigation to mint the request — not a standalone curl.

---

## Fast path that *does* work (~10–14s vs ~20s+)

1. Ensure signed-in + **Pro** selected once.
2. `page.goto(udm=50 URL, waitUntil: 'commit')` — don’t wait for full load.
3. Poll `main.innerText` every ~400ms.
4. **Early-stop** when answer is useful (don’t wait for “AI Mode response is ready” footer):
   - body length ≳ 1800, and
   - has ratings (`4.x`) and prices / “Must-Order” / table-ish text  
   **or** footer ready string appears.
5. Slice from `AI Mode Conversation` onward; save dump; write compact guide.

Measured: useful Pro answer ~**12s** with early-stop vs ~**18s+** waiting for ready footer.

Helper: [`aimode-extract.js`](aimode-extract.js) — run inside Playwright `page.evaluate` / agent `browser_run_code`.

### URL template

```
https://www.google.com/search?udm=50&hl=en&q=<urlencoded prompt>
```

### Extract snippet (DOM)

```js
const t = (document.querySelector('main') || document.body).innerText || '';
const i = t.indexOf('AI Mode Conversation');
return i >= 0 ? t.slice(i) : t;
```

---

## Agent checklist (food city research)

1. Confirm account chip (signed in).
2. Select **Pro** if not checked.
3. Run one tight prompt (local food, 4.5★+, value>service, neighborhoods, must-order, local currency + USD). Expand to nature / lodging / transit / money / nights when building a full hub guide.
4. Early-stop extract → `memory/restaurant-previews/playwright-<city>.txt`.
5. Write compact `memory/<city>-local-food.md` (standalone book — see project `.github/copilot-instructions.md`).
6. **Wire the entry point** — do not stop at the sub-md. Per copilot-instructions:
   - `itinerary.md` §4 hub blurb + single `**Guide:**` link (no TOC spam)
   - §1 baseline table if default/flex/core idea/nights changed (re-sum ~83n / ≤90)
   - §6 costs + §7 lodging one-liner when beds/$/day change
   - `memory/scandi-transit.md` + `memory/scandi-money-tips.md` indexes
   - `RESUME.md` guide list if needed
7. Optional follow-up query only if gaps (don’t thrash).

---

## Personal use only

Session cookies + BotGuard are **your** Google account. Do not export cookies into the repo. Do not use on accounts you don’t own. Endpoints rotate; prefer DOM extract over hardcoded RPC names.
