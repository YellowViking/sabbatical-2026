# Sabbatical 2026 — agent instructions

Planning repo for a Europe fall sabbatical (Schengen-aware). **Not a software app** — markdown is the product.

## Entry point (always)

| Priority | File | Role |
|---|---|---|
| **1 — start here** | [`itinerary.md`](../itinerary.md) | **Canonical hub:** route order, night defaults/ranges, costs, lodging shortlist, open items |
| 2 | [`RESUME.md`](../RESUME.md) | Session handoff for a new agent |
| 3 | `memory/*-local-food.md` | Per-hub deep guides (detail lives here) |
| 4 | `memory/scandi-*.md` | Cross-cutting indexes (transit, money, off-beat) |
| 5 | [`memory/europe-year-base-nomad.md`](../memory/europe-year-base-nomad.md) | **Parallel goal:** ~1-year base (sabbatical/savings; not fall ≤90 hop) |
| 6 | [`memory/spain-nlv-vs-france-visitor.md`](../memory/spain-nlv-vs-france-visitor.md) | Spain NLV vs France VLS-T means-visa deep dive |

**Rule:** After any substantive trip-planning change, **`itinerary.md` must still be a valid single-file overview.** Deep content goes in `memory/`; the itinerary **summarizes + links**, it does not go stale while a sub-doc is fresh.

Do **not** invent a parallel master plan in chat-only notes. Prefer editing files.

---

## Document graph (how `.md` files link)

```text
itinerary.md                          ← ENTRY / source of truth for tables
├── §1 baseline table (nights)
├── §4 hub blurbs  ──Guide:──►  memory/<hub>-local-food.md
├── §6 costs table
├── §7 lodging bullets  ──Detail:──►  same guide #lodging…
├── TOC links ──► memory/scandi-transit.md
│                 memory/scandi-money-tips.md
│                 memory/scandinavia-optional-offbeat.md
└── §8 locked outcomes (decisions only — no research trail)

memory/<hub>-local-food.md            ← full city book
├── links up to itinerary concepts (§6/§7 criteria)
├── Getting around → scandi-transit.md (spine index)
├── Money savers → scandi-money-tips.md (country rules)
└── Optional → scandinavia-optional-offbeat.md

memory/scandi-transit.md              ← all-legs + apps index
└── lists every city guide

memory/scandi-money-tips.md           ← DK/SE/NO rules + city money anchors
└── links each guide #money-savers

memory/europe-year-base-nomad.md      ← year-base / nomad legal+city shortlist
memory/restaurant-previews/           ← research dumps (usually untracked)
skills/                               ← Playwright research how-tos

**Year-base rule:** fall city guides may include a short **Year-base scout** section (workday test, cowork, winter honesty). Do not imply Schengen tourist days = a 12-month right to stay. Deep visa comparison lives only in `europe-year-base-nomad.md` + itinerary one-liners.
```

**Hub code ↔ file**

| Code | Guide path |
|---|---|
| CPH | `memory/copenhagen-local-food.md` |
| GOT | `memory/gothenburg-local-food.md` |
| OSL | `memory/oslo-local-food.md` |
| SVG | `memory/stavanger-local-food.md` |
| BGO | `memory/bergen-local-food.md` |
| STO | `memory/stockholm-local-food.md` |
| Visby | `memory/gotland-local-food.md` (**optional** stop / thin card) |
| HEL | `memory/helsinki-local-food.md` (**optional** thin guide; on spine) |
| TLL | `memory/tallinn-local-food.md` |
| RIX | `memory/riga-local-food.md` (sponge + year-base scout) |
| VNO | `memory/vilnius-local-food.md` |
| SI | `memory/slovenia-local-food.md` (LJU + Bled/Bohinj split) |
| HR | `memory/croatia-local-food.md` (ZG · Plitvice · Split · DBV) |
| IT / … | add `memory/<name>-local-food.md` when written |

---

## Updating the **baseline nights table** (`itinerary.md` §1)

Table columns: `Phase | Stop | Default | Flex range | Core idea / if you stretch`

When **default** or **flex** nights change for any stop:

1. **Edit the §1 baseline row** (Default + Flex range + short core idea).
2. **Re-sum Schengen:** default nights should still target **~83n baseline**, hard cap **≤90**. Update the “Default sum ~Nn” line if the sum moved.
3. **Swing pool** (§1 flexibility rules): if you moved nights into/out of Gotland / Riga / Bergen / CPH, adjust the swing-pool blurb.
4. **Mirror in §4 hub heading:**  
   `### <Stop> — default **Xn** · flex **A–Bn**`  
   must match the table.
5. **Mirror in the city guide** (if it exists): title line + Flexible fit “Nights” row + Length→plan table.
6. **§6 costs table:** same `Nights` count × revisit `~All-in/day` if lodging/food assumptions changed → recalc **Subtotal** and **On-the-ground** total + blended $/day.
7. **Off-beat doc** `memory/scandinavia-optional-offbeat.md` per-stop default/flex row if present.
8. **Optional:** `RESUME.md` route one-liner if defaults readers rely on.

**Do not** change only the city guide nights and leave §1 wrong.

### Nights consensus (Gemini / research)

When validating lengths with Google AI Mode:

- Write a **Nights consensus** subsection in the city guide (see Stockholm).
- Add a short note under the §4 hub blurb **and** one **outcome row** in §8 if it changes policy (e.g. “cut Gotland before STO”) — not a research write-up.
- Keep **flex range** as the operational answer; default is the planning anchor.

---

## Updating **§4 hub blurbs** (itinerary ↔ guide)

Each finished hub should have:

1. Heading with **default · flex** matching §1.
2. 2–5 lines: what to do, food lean, bed lean, kill-list (skip X).
3. **Exactly one** deep link, pattern:  
   `**Guide:** [food · nature · lodging · transit · money](memory/<hub>-local-food.md).`  
   Add `· nights` only if a consensus section exists.
4. No second competing “master” paragraph that contradicts the guide.

When the **guide** gains lodging / transit / money / nights:

- Refresh the §4 blurb keywords (beds ⭐ one-liner, food traps, transit app).
- **§7** stays method-only — ensure the guide is linked from §4 / §7 index table; do not dump the shortlist into §7.
- Refresh **§6** day-rate if the money model changed.
- Add guide to indexes: `scandi-transit.md` Guides line · `scandi-money-tips.md` table · `RESUME.md` list if needed.

---

## Updating **§6 costs table**

Columns: `Region | Nights | Lodging lean | ~All-in/day | Subtotal`

| Trigger | Action |
|---|---|
| Nights change | Update Nights + Subtotal (`nights × day`) |
| Hostel vs hotel lean changes | Update Lodging lean + All-in/day + Subtotal |
| New researched city costs | Replace “mid” placeholder with lean note |
| Transport spikes (shuttle, Flåm) | Keep in transport/sightseeing notes — don’t double-count into every day-rate unless intentional |

After edits: recompute **On-the-ground** sum, blended $/day, and the **Band** rows (hostel-lean total ≈ ground + ~$2k transport). Update `RESUME.md` cost one-liner if the headline band moved.

---

## Updating **§7 lodging**

**`itinerary.md` §7 stays thin:** policy summary + search/verify method + index of guide lodging anchors. **Do not** paste full per-city shortlists, score tables, or multi-bed bullets into §7.

- **Full shortlist** (⭐ + alts, neighborhood, avoid, curtains, kitchen, **Maps links only** in user-facing tables) lives in `memory/<hub>-local-food.md` → Lodging.
- **§4 hub blurb** may keep **one line** of bed lean (⭐ name) — not the whole table.
- When beds change: **edit the city guide first**, then refresh §4 one-liner if the ⭐ moved; touch §7 only if **policy/method** changed.
- **Verify on ≥2 primaries before ⭐:** **Google Maps** (≳4.0★ + count) **and** **Booking.com** (≳8.0 + count). **Hostelworld** for backpacker hostels when listed. **Do not** ⭐ from AI Mode/Gemini alone.
- If sources disagree, prefer the **larger sample** and skim recent 1–3★ themes (noise, dirt, bugs, bait-and-switch).
- **Demote/remove** Maps **&lt;4.0★**, Booking **&lt;8.0**, closed, or tiny sample (n ≲ 30) unless explicitly flagged thin-data alt.
- Known Baltic correction (Aug 2026): **Imaginary Hostel TLL — not a pick**; prefer Fat Margaret’s / Viru / Munkenhof (detail only in Tallinn guide).

---

## New city / hub guide checklist

Use when adding Gotland, Helsinki, Tallinn, etc.

### A. Research (optional but preferred)
- Google AI Mode Pro via `skills/google-ai-mode-research/` (food, nature, lodging, transit last-mile, money, **nights consensus**).
- Dumps → `memory/restaurant-previews/` (keep untracked unless asked to commit).

### B. Create `memory/<hub>-local-food.md`
Standalone book with sections (order used on Scandi spine):

1. Title: default **Nn** · flex **A–Bn** · currency · links to transit + money indexes  
2. **Flexible fit** + Length→plan (+ **Nights consensus** if researched)  
3. **Getting around** (apps, arrive/leave, bed→sights, bed→food)  
4. Sample plan skeleton  
5. Nature · city/museums · Food  
6. **Lodging**  
7. **Money savers**  
8. Optional / off-beat link  

Link **up** to spine indexes; do not depend on chat history.

### C. Wire `itinerary.md` (mandatory)
- [ ] §1 baseline row (or confirm unchanged)  
- [ ] §4 hub blurb + **Guide:** link  
- [ ] §6 nights + day-rate if in cost table  
- [ ] §7 index row / method only (full beds in guide; §4 ⭐ one-liner)  
- [ ] TOC / top “Transit · Money” links only if new **index** files (not every city)  
- [ ] §8 outcome row if nights/policy locked (no process essay)  

### D. Wire indexes
- [ ] `memory/scandi-transit.md` — apps row if new country/city system; intercity leg; Guides list  
- [ ] `memory/scandi-money-tips.md` — city row → `#money-savers`  
- [ ] `memory/scandinavia-optional-offbeat.md` — default/flex row if Scandi  
- [ ] `RESUME.md` — guide list / cost band if needed  

### E. Consistency pass
- [ ] §1 default == §4 heading == guide title nights  
- [ ] Sum of §1 defaults still coherent with §6 nights column  
- [ ] No orphan guide (exists on disk but no itinerary link)  
- [ ] No itinerary “Guide:” pointing at a missing file  

---

## Style constraints (this repo)

- **Nature-first**, value > tourist service; note ⚠️ on classics below ~4.5★ kept for value.  
- **Flexible nights**, not fixed calendar vows; order of spine stays NW→SE.  
- Prefer **free-cancellation** beds; flag sell-outs (Flåm, Preikestolen shuttle, Vy, Gotland ferry).  
- Keep itinerary hub blurbs **short**; depth in `memory/`.  
- Avoid TOC spam and giant dumps in `itinerary.md`.  
- FX ballparks: ~6.9 DKK/$ · ~10.5 SEK/$ · ~10.5–11 NOK/$.  
- Research: signed-in Playwright + AI Mode Pro when doing live Google work (`skills/google-ai-mode-research/`).  
- Do not commit secrets, cookies, or `.playwright-mcp/` noise; prefer not to commit `restaurant-previews/` unless asked.

---

## Quick “did I keep the entry point honest?”

Before ending a turn that touched trip content:

1. Open `itinerary.md` — would a cold reader see the new truth in §1/§4/§6/§7?  
2. Click (or verify path of) every **Guide:** / **Detail:** you added.  
3. If only a sub-md changed something load-bearing (nights, ⭐ bed, $/day), **promote a one-line summary** into the itinerary.
