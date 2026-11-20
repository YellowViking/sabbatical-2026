# Agent instructions: travel-planning repo

This repo holds trip logs, city guides and research for long, solo, budget, train-first trips, plus the automation that plans them. **It isn't a software app: the markdown is the product.** Read [`AGENTS.md`](../AGENTS.md) too, for the API-first browser rules, known booking/fare endpoints and traveller preferences.

## Layout

| Path | What it is |
|---|---|
| [`README.md`](../README.md) | Landing page and index. Keep it in sync whenever a trip, guide or research note is added or renamed |
| `trips/<trip>/README.md` | One trip: route table, how it was planned, lessons. A finished trip records **what happened**; a trip being planned records the current plan |
| `trips/<trip>/guides/<place>.md` | One city or region guide per file (food, drinks, sights, hikes, getting around, where to sleep, money) |
| [`research/`](../research/) | Reusable notes not tied to one place: packing, points, visas, long-stay bases, hiking routes |
| [`skills/`](../skills/) | Playwright/CDP how-tos and scripts (Maps lists, AI Mode research, Sheets, card expense sync) |
| [`or-cost-monitor/`](../or-cost-monitor/) | Separate cost-monitoring tool |

## Rules for trip files

- **One source of truth per trip:** `trips/<trip>/README.md`. Detail lives in the guides; the trip README summarises and links. Don't keep a parallel plan in chat-only notes, and don't add new root-level status files (no RESUME, next-bookings or similar).
- **While a trip is live,** booked/pending markers are fine in the trip README. **When it ends,** rewrite the README as the record of what happened and make the guides timeless. Remove "today / tomorrow / pending / unbooked / last checked" lines. Prices stay, with the month and year they were seen.
- **New guide checklist:**
  1. Create `trips/<trip>/guides/<place>.md`.
  2. Link it from the trip README's route table and from the root `README.md` guide index.
  3. Check that no link dangles.
- **Guide sections, in order:** title + how many nights it deserves → getting around (arrive/leave, local transit app) → sights (free first; mark paid ones and say why they're worth it) → hikes/nature (AllTrails rating + review count, trailhead transport) → food (locals' price vs tourist price) → drinks (craft beer, cheap bars, wine) → where to sleep → money savers. Use Google Maps place links.
- **Vetting beds:**
  - Verify on at least two primary sources: Google Maps (≳4.0★ with its review count) and Booking (≳8.0 with its count), plus Hostelworld for hostels. Read the full score spread and recent 1–3★ reviews (noise, dirt, bugs).
  - Compare **checkout totals including city tax and coupons** across Booking, Agoda, Hostelworld and the property's **own booking engine**.
  - Never pick a bed on an AI summary alone.
- **Public repo:** no booking references, PNRs, check-in codes, card or personal-spending data, cookies, tokens or captured request bodies. Raw research dumps and screenshots stay out of the repo (keep them under `~/.local/share/`).

## Live web research / booking automation

Start from an API, not from clicks (see `AGENTS.md`). The default browser path is Playwright over CDP on `:9222` (`~/.local/share/cdp-tools/pw.mjs`). Use Google AI Mode (`skills/google-ai-mode-research/`) only for leads, and confirm facts on official sites.
- **Flights:** scan every practical gateway for both cash and award fares. Rank on onward cost and time, self-transfer risk, backtracking and season before live-confirming the finalist.
- Follow the repo's Maps, AI Mode and Sheets skills before inventing a new browser workflow. Stop any booking flow before passenger or payment details unless the traveller says to go ahead.
