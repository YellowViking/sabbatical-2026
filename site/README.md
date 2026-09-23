# site/

A static web version of [`itinerary.md`](../itinerary.md).

**Live:** https://sabbatical-2026-beta.vercel.app

The page carries the itinerary's content verbatim — all ten sections plus the
appendix, every table, every named bed and trail. It adds no travel facts of its
own. What it adds is structure: the 90-day Schengen cap as a visual ledger, a
colour ramp that tracks the route north-to-south, and calendar dates derived
from the ticketed landing.

## Design notes

**The ledger is the hero.** The document's governing constraint is the 90-day
Schengen window, so the page opens with 90 cells: 83 filled by stop, 7 left
outlined as buffer. Hovering a cell names its day and date.

**The colour ramp is the route.** Fjord teal at Copenhagen warms to rust by
Amalfi, encoding both the north-to-south spine and late-August-to-November at
once. The same ramp keys the ledger, the route rail, the baseline-table dots and
each hub card.

**Night meters show flex, not just defaults.** `6n default · flex 4–7n` renders
as filled cells (committed), soft cells (trimmable) and outlined cells (stretch),
so the shape of a stop's flexibility is visible without reading the range.

Type is Familjen Grotesk for display, Newsreader for prose, IBM Plex Mono for
every figure and date — so numbers read as a timetable rather than body copy.

## Dates are derived, not authored

`itinerary.md` deliberately gives night counts rather than fixed dates ("dates
slide when you move nights"). The site computes them from the two facts the
document does fix: the ticketed **Aug 24** landing, and the baseline default
night counts.

    Aug 24 (Schengen day 1) + 83 nights → Nov 15 departure
    Schengen day 90                     → Nov 21 hard exit

They appear in the baseline table, on each hub card, in the route rail and on
all 90 ledger cells, labelled as derived throughout. Change a night count and
every date downstream shifts with it.

## Structure

    site/
      index.html         all prose and tables, authored by hand from itinerary.md
      app.js             STOPS[] — the single source of truth for nights and dates
      styles.css         design tokens and layout
      images/            14 photographs + credits.json (provenance)
      fetch-images.mjs   the script that fetched them
      vercel.json        static hosting config

`index.html` holds the prose. `app.js` holds the numbers: the ledger, the route
rail, the baseline table rows and every night meter all render from one `STOPS`
array, so a night count cannot disagree with itself across the page. A guard
warns in the console if the defaults stop summing to 83.

## Running it

Any static server works — there is no build step:

    cd site
    python -m http.server 4321
    # → http://localhost:4321

## Keeping it in sync with itinerary.md

When the itinerary changes:

1. Night counts, flex ranges and phases → edit `STOPS` in `app.js`. Dates,
   the ledger and the rail follow automatically.
2. Prose, tables and bullets → edit `index.html`.
3. Re-check that defaults still sum to 83 (the console guard will tell you).

## Photographs

Fourteen images from Wikimedia Commons, fetched by `fetch-images.mjs`. Full
provenance — source file, author and licence — is in `images/credits.json`, and
attribution is rendered in the page footer as the licences require.

Licences are a mix of CC BY, CC BY-SA, CC0 and public domain. Any reuse should
carry the same attribution; check `credits.json` for the per-image terms.

## Deploying

    npx vercel deploy --prod

Static, no build step, no dependencies. Images are lazy-loaded and cached for a
year via `vercel.json`; first paint carries only markup, CSS, JS and fonts.
