---
name: google-maps-saved-places
description: >
  Bulk-save Google Maps places into the signed-in user's Saved lists. For this
  user, default target list is **"Want to go"** (not "Saved places") unless they
  ask otherwise. Also supports Favorites / custom lists via Maps' internal web
  endpoint from a logged-in browser session. Use for itinerary sights without
  slow UI click-loops. Prefer createitem batch path. Requires Chrome DevTools
  MCP / Playwright on an already-logged-in Chrome profile.
---

# Google Maps Saved places (internal web API)

## What this is / when to use it

Google does **not** expose a public "add to Saved places" API for personal
accounts. The Maps web app saves places via:

```
GET https://www.google.com/maps/preview/entitylist/createitem
    ?authuser=0&hl=en&gl=us&pb=...
```

From JavaScript **inside a logged-in `google.com/maps` tab**
(`credentials: "include"`), you can harvest one real save URL, then mutate only
the place fields and batch-save dozens of sights in seconds.

Use this when the user wants to:
- Dump an itinerary's sights into **Saved places** (or another list)
- Avoid per-place UI: search → open → Save → pick list
- Reuse the same path across cities on a trip

> ⚠️ **Undocumented, personal-use only.** Runs against *your* account with
> *your* session cookies. Can break when Maps ships a new build. Rate-limit
> politely (~50–100 ms between calls). Never use on accounts you don't own.

---

## Prerequisites

1. **Logged-in Chrome** with the user's Google account (Maps must show avatar,
   not "Sign in").
2. **Browser automation attached to that session**, not a fresh profile:
   - Preferred: `chrome-devtools-mcp` with `--autoConnect` after enabling
     remote debugging at `chrome://inspect/#remote-debugging`
   - Or Playwright CDP to the same Chrome
3. Copilot/agent built-in browser tools often open an **unsigned** session —
   do **not** use those for this skill.

### VS Code MCP snippet (user `mcp.json`)

```json
{
  "servers": {
    "chrome-devtools": {
      "type": "stdio",
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--autoConnect",
        "--no-usage-statistics"
      ]
    }
  }
}
```

---

## CRITICAL: what is STABLE vs what ROTATES

**STABLE (safe to rely on):**
- Endpoint path: `/maps/preview/entitylist/createitem`
- Success body: starts with `)]}'` then `[]` (or similar empty XSSI-prefixed JSON), HTTP **200**
- Missing/invalid session tail → HTTP **400** HTML error page
- Feature id format in place URLs: `1s0xHEX1:0xHEX2`
- Decimal form in `pb`: `!1y<dec1>!2y<dec2>` where dec = `BigInt("0x"+hex).toString(10)`
- Coords in `pb`: `!3d<lat>!4d<lng>`
- Place name in `pb`: `!3s<url-encoded-name-with-+-for-space>`
- List id appears as `!1s<LIST_ID>` near the start of `pb`
- Built-in list **type labels** in client JS (for reading, not always in createitem):
  - `1` Favorites
  - `2` Want to go
  - `4` Starred places
  - `7` Travel plans
  - Custom lists / **Saved places** use a **list id string** + type code (Saved places observed as `!2e6` with id)

**ROTATES / account-specific (re-harvest every session or when 400s appear):**
- Session tail tokens in `pb` (`!3m6!1s...`, `!2z...`, `!4s...`, `!4m1!2i...`)
- Exact `pb` field ordering / extra flags (`!7e81!28e2`, etc.)
- List id for "Saved places" (**per account** — do not hardcode forever)
- Obfuscated JS action names (`pane.wfvdle53`, etc.)

**Consequence:** always **harvest one live createitem URL** from a real UI save
in the current session, then mutate place fields. Don't invent the session tail.

---

## Recipe (fast path)

### Step 0 — Open Maps signed in

```js
// In chrome-devtools MCP / page evaluate:
location.href = 'https://www.google.com/maps';
// Confirm avatar present, no Sign-in link
```

### Step 1 — Harvest a template `createitem` URL

1. Open any real place card (must show **Save**, not a broken empty place).
2. Install an XHR/fetch hook **before** clicking Save.
3. Click **Save** → choose target list (**Saved places** unless user says otherwise).
4. Capture the request URL containing `entitylist/createitem`.

```js
const captured = [];
const xo = XMLHttpRequest.prototype.open;
XMLHttpRequest.prototype.open = function (m, u, ...r) {
  if (String(u).includes('entitylist/createitem')) captured.push(String(u));
  return xo.call(this, m, u, ...r);
};
// …click Save → "Saved places"…
// template = captured[0]  (may be path-only; prefix location.origin if needed)
```

**Example shape (tokens redacted):**
```
/maps/preview/entitylist/createitem?authuser=0&hl=en&gl=us&pb=
  !1m8!1s<LIST_ID>!2e6!3m1!1e1!3m1!1e9!3m1!1e15
  !2m14!2m6!6m2!3d<LAT>!4d<LNG>!7m2!1y<Y1>!2y<Y2>!3s<NAME>
  !9m5!1m1!1e1!2m2!1y<Y1>!2y<Y2>
  !3m6!1s<SESSION>!2z<SESSION>!4m1!2i<N>!7e81!28e2!4s<SESSION>
```

Parse out:
- `LIST_ID` from `!1s...`
- Keep the **entire** `pb` as template (including session tail)

### Step 2 — Resolve each place → `{name, lat, lng, y1, y2}`

**Preferred:** place URL already known:
```
.../place/Name/@LAT,LNG,17z/data=!...!1s0xHEX1:0xHEX2!8m2!3dLAT!4dLNG...
```

```js
function parseFeature(hexPair /* "0xAAA:0xBBB" or "1s0xAAA:0xBBB" */) {
  const m = hexPair.match(/0x([0-9a-fA-F]+):0x([0-9a-fA-F]+)/i);
  return {
    y1: BigInt('0x' + m[1]).toString(10),
    y2: BigInt('0x' + m[2]).toString(10),
  };
}
```

**Search fallback** (from the Maps tab):
```js
async function resolvePlace(query) {
  const url = `https://www.google.com/s?tbm=map&gs_ri=maps&suggest=p&authuser=0&hl=en&gl=us&q=${encodeURIComponent(query)}`;
  const t = await (await fetch(url, { credentials: 'include' })).text();
  const feat = t.match(/0x[0-9a-fA-F]+:0x[0-9a-fA-F]+/);
  const coord = t.match(/\[null,null,(-?\d+\.\d+),(-?\d+\.\d+)\]/);
  // parse feature → y1/y2; coord → lat/lng; name from query or suggest blob
  return { query, lat, lng, ...parseFeature(feat[0]), name };
}
```

If suggest is messy, navigate once to the place UI and read `location.href` + `h1`.

### Step 3 — Mutate template and batch save

```js
function buildCreateItemUrl(templateUrl, { lat, lng, y1, y2, name, listId }) {
  let url = templateUrl;
  // optional: force list id
  if (listId) url = url.replace(/(!1m8!1s)[^!]+/, `$1${listId}`);
  url = url.replace(/!3d-?\d+(?:\.\d+)?!4d-?\d+(?:\.\d+)?/, `!3d${lat}!4d${lng}`);
  url = url.replace(/!1y\d+!2y\d+/g, `!1y${y1}!2y${y2}`);
  url = url.replace(
    /!3s[^!]+!9m5/,
    `!3s${encodeURIComponent(name).replace(/%20/g, '+')}!9m5`
  );
  return url;
}

async function savePlace(templateUrl, place) {
  const url = buildCreateItemUrl(templateUrl, place);
  const res = await fetch(url, {
    credentials: 'include',
    headers: { accept: '*/*', 'x-same-domain': '1' },
  });
  const text = await res.text();
  const ok = res.status === 200 && text.includes(")]}'");
  return { name: place.name, status: res.status, ok, resp: text.slice(0, 80) };
}

// Serial with small delay (safer than huge parallel)
for (const p of places) {
  await savePlace(template, p);
  await new Promise((r) => setTimeout(r, 60));
}
```

**Do not strip the session tail.** A minimal `pb` with only list+coords+feature
returns **400**.

### Step 4 — Verify

UI: left rail **Saved** → open **Saved places** → confirm names + count.

Or search page text:
```js
const t = document.body.innerText;
places.every((p) => t.toLowerCase().includes(p.name.toLowerCase()));
```

---

## Choosing the list

| User intent | What to click when harvesting | Notes |
|---|---|---|
| Default for this user | **Want to go** | Preferred trip list (large); harvest that row |
| Explicit "Saved places" | **Saved places** | Only if user asks |
| Favorites / Starred / custom | That list name | Template's `!1s` becomes that list's id |

**Observed list ids (this account, 2026-07 — re-harvest if stale):**
- Want to go: `VRmowV-NH-2D2_4w7nZiG3xnMt49fg` (`!2e3`)
- Saved places: `14fdX2NB-Kkhll4HZWj2rM2vxYgI3A` (`!2e6`)

**Do not create a new list** unless the user asks. Empty "Untitled list" leftovers
should be deleted if accidentally created.

---

## Failure modes & fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| HTTP 400 HTML | Session tail missing/expired | Re-harvest createitem from UI |
| HTTP 200 but place missing | Wrong list id / wrong feature id | Verify feature from place URL; re-open Saved places list |
| Save menu only "New list" | Place card empty / no feature | Open a full `/maps/place/...!1s0x...` URL first |
| Suggest has no `0x…:0x…` | Ambiguous query | Add city name; or open place UI once |
| Tools on signed-out Maps | Wrong browser context | Use `--autoConnect` Chrome, not built-in unsigned browser |
| `Illegal invocation` on XHR hook | Bad prototype patch | Patch carefully; prefer capturing URL from one UI save only |

---

## Discovery (if endpoint moves)

1. Open DevTools Network on maps.google.com while saving a place.
2. Filter: `createitem`, `entitylist`, `placelist`, `shortlist`.
3. Note method (currently GET), query param name (`pb`), and which fields change
   when saving two different places (those are place fields; the rest is session/list).
4. Optionally search loaded `maps.m.*.js` for `entitylist/createitem`,
   `Saved places`, `Want to go` to confirm list-type enums.

Client JS (observed) builds batchexecute URLs under
`` `${WIZ_global_data.eptZe}data/batchexecute` `` (`eptZe` ≈ `/maps/_/MapsWizUi/`)
for some list operations; **createitem preview** is the fast save path that
worked for bulk add.

---

## Worked example (Copenhagen first days, 2026-07)

Account Saved places list id (snapshot): `14fdX2NB-Kkhll4HZWj2rM2vxYgI3A`

Saved via batch createitem:
- Nyhavn
- Tivoli Gardens
- Rosenborg Castle
- Freetown Christiania
- Louisiana Museum of Modern Art
- Turning Torso (Malmö)
- Lund Cathedral

Count moved **3 → ~9–10**; all names visible under Saved places.

---

## Agent checklist

- [ ] Chrome remote debugging / autoConnect to **logged-in** profile
- [ ] User confirmed target list (default **Saved places**)
- [ ] Harvest fresh createitem template this session
- [ ] Resolve feature ids + coords for each place
- [ ] Batch fetch with session tail preserved
- [ ] Verify names in Saved places UI
- [ ] Don't leave accidental Untitled lists
- [ ] Don't print full session tokens into git commits / public logs
