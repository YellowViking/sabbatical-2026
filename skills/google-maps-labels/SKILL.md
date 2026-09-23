---
name: google-maps-labels
description: >
  Create Google Maps **personal labels** ("Add a label") on coordinate
  pins for places that have no business listing — i.e. apartments, private
  rooms, and units inside residential buildings whose Booking/address exists
  on Maps but which have no named Maps entity. Use when the user asks to
  "label" accommodations on Maps, or when bulk-saving a shortlist of
  listing-less rentals that Maps cannot find by name. Requires a
  logged-in Playwright/Chrome session. Verified Sep 2026.
---

# Google Maps personal labels (UI automation)

## What this is / when to use it

Many short-stay apartments have **no Google Maps business listing**. Their
street address resolves as an **address / coordinate pin**, but searching the
property name returns generic hotels or nothing. You cannot "Save" them as
places and they are not findable by name.

**Personal labels** attach a private name to such a pin so it is
identifiable when you return to it. This is the modern replacement for the
old "Your places → Labeled" feature.

Use when the user wants:
- Accommodation shortlists **labeled on Maps** (not dumped into a list)
- Listing-less rentals/guesthouse units made **identifiable at the address**
- A private nickname on a dropped/coordinate pin

> ⚠️ Undocumented UI feature, personal-use only. Runs against *your* account in
> *your* session. Can change when Maps ships a new build. No stable internal
> endpoint was found — this is **UI-driven** (see "Why not an API").

---

## Prerequisites

1. **Logged-in Chrome** (Maps shows avatar, not "Sign in").
2. Browser automation attached to that session — Playwright MCP
   (`@playwright/mcp --browser chrome`) or chrome-devtools-mcp `--autoConnect`.
3. Copilot built-in browser tools open a **fresh unsigned** session — do **not**
   use them for account actions.

---

## CRITICAL: where "Add a label" appears

**IT ONLY APPEARS ON COORDINATE / ADDRESS PINS — NOT ON BUSINESS LISTINGS.**

| Pin type | Place-card action row | "Add a label"? |
|---|---|---|
| **Coordinate / dropped pin** (e.g. `.../place/56.95,24.12/…`) | `Add a missing place · Add your business · **Add a label** · Your Maps history` | ✅ **YES** |
| **Business listing** (has a real Maps entity, e.g. `Compact Studio next to JRT`) | `Directions · Save · Nearby · Share` + only `Your Maps history` | ❌ **NO** |

**Consequence:** if a property already has a **named Maps listing**, you don't
need a label — it's findable by name. Labels are only for the
**address-only** ones.

### How to tell which you have
Search the property **name** on Maps:
- **Direct listing** → `h1` is the name, with rating/photos/website.
- **No listing** → `h1` is `Results` (generic hotels), or "Maps can't find …".

Then open the **address** pin via its coordinates (see Step 1) to get the
label action.

---

## Recipe

### Step 1 — Open the coordinate pin

Use the bare lat/lng form (most reliable for surfacing the label action):

```
https://www.google.com/maps/place/<LAT>,<LNG>/@<LAT>,<LNG>,17z?hl=en
```

Get `<LAT>,<LNG>` from either:
- The address pin: `…/place/<Address>/@<LAT>,<LNG>,17z/…`
- A place URL: `!8m2!3d<LAT>!4d<LNG>` (the `3d/4d` = pin, not `@` = viewport)

### Step 2 — Click "Add a label"

```js
await page.getByRole('button', { name: 'Add a label' }).click();
```

Panel opens with:
- `heading "Add a label"` (h1)
- `combobox "Add a label"` ← the input
- `button "Cancel"`
- Note text: *"Personal places will be used across Google products…"*

### Step 3 — Type + commit

```js
const cb = page.getByRole('combobox', { name: 'Add a label' });
await cb.fill('M6 Rooms (Merkela 6)');
await cb.press('Enter');           // commit
```

**Success signal:** page text contains `Created label <name>.`

### Step 4 — Verify

Re-open the **same lat/lng** and read the card heading:

```js
await page.goto(`https://www.google.com/maps/place/${lat},${lng}/@${lat},${lng},17z?hl=en`);
const h1 = await page.locator('h1').first().innerText();  // → your label
```

The label becomes the pin's **h1** on the card. ✅ confirmed Sep 2026.

---

## Reusable batch script

See [`batch-label.js`](batch-label.js). Run inside Playwright MCP via
`browser_run_code_unsafe` (it drives `page`), or adapt to a script:

```js
await page.evaluate(...)   // not used — needs Playwright page, not DOM JS
```

Loop shape (worked reliably for 3+ in one run, ~4 s each):

```js
for (const t of targets) {
  await page.goto(`https://www.google.com/maps/place/${t.lat},${t.lng}/@${t.lat},${t.lng},17z?hl=en`);
  await page.waitForTimeout(3500);
  await page.getByRole('button', { name: 'Add a label' }).click();
  await page.waitForTimeout(1200);
  const cb = page.getByRole('combobox', { name: 'Add a label' });
  await cb.waitFor({ timeout: 5000 });
  await cb.fill(t.label);
  await cb.press('Enter');
  await page.waitForTimeout(1800);
  // assert body text matched /Created label/ or record failure
}
```

---

## GOTCHAS (learned the hard way)

1. **Labels are NOT searchable by name.** Typing the label into the Maps search
   box returns unrelated businesses. Labels surface on the **pin/card** and in
   history — not as search results. To retrieve one, search the **address** or
   open the coordinates.
2. **No label action on business listings.** If you can't find the button,
   you're on a listing → just use the name.
3. **The button is a real `<button>`, not the map-layer "Labels" toggle.**
   The word "Labels" also appears in the map-type/layers control — ignore it.
   The right one sits in the place-card action row next to *Add your business*.
4. **`h1.YV5VMd` is the transient panel heading.** After commit it disappears
   and the label becomes the card `h1`. Don't key assertions on the class.
5. **Address vs coordinate:** opening the *address* (`/place/Krišjāņa Barona iela 21a/…`)
   may show a Directions-style card **without** the label action. Force the
   bare `lat,lng` form to get it.
6. Labels are **private** to your account.
7. Don't confuse with **Saved lists** — see sibling skill
   [`../google-maps-saved-places/SKILL.md`](../google-maps-saved-places/SKILL.md).
   Lists = collections (searchable, shareable); labels = private name on one pin.

---

## Why not an API

Unlike Maps `createitem` (Saved lists), **no stable internal endpoint was found
for labels** in this session. It is not the same class of problem as
batch-saving — treat labels as **UI-only**. If revisiting, look for a
`entitylist`/`placelabel`-style XHR fired on the label commit and harvest it the
same way as the createitem template.

---

## Worked example (Riga, Sep 2026)

Four apartment picks with **address-only** pins → labeled:

| Property | Address | Label created |
|---|---|---|
| City Nest Riga Center – Self Check-in | Kr. Barona iela 21a | `City Nest (Kr. Barona 21a)` |
| M6 Rooms Riga | Merķeļa iela 6 | `M6 Rooms (Merkela 6)` |
| Modern Loft Studio in Old Town | Pasta iela 6 | `Modern Loft Studio (Pasta 6)` |
| M9 City Centre apartments | Marijas iela 9 | `M9 Apartments (Marijas 9)` |

Fifth pick **Compact Studio next to JRT** already had a **named listing** → no
label needed.

**Pattern:** for a shortlist, first check each name on Maps; label only the ones
that resolve to `Results`/address pins.
