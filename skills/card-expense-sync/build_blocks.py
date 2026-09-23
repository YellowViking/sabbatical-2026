#!/usr/bin/env python3
"""Turn sheet-rows.csv into a paste job that fills macro-created week blocks.

    python3 build_blocks.py --first-row 684 --sheet-url "https://docs.google.com/…"

IMPORTANT — run the sheet's own `newweek` macro FIRST, once per week block you need.
Do not hand-build the block. The macro (Extensions > Macros > "new week", Cmd+Opt+Shift+1)
copies the `WeeklyTemplate` named range, stamps `Week <N>`, and increments `Metadata!CurrentWeek`.
Building blocks by pasting a TSV skips all three and, worse, wipes the Country/Currency
data-validation dropdowns.

Blocks are 11 rows with one blank row between them, so block N+1 starts 12 rows below block N:

    r+0   Week N | Currency: | USD | =VLOOKUP(C{r},pairs,2,FALSE)
    r+1   Day | Food&Drink | Lodging | Transportation | Other (tickets/tours etc) | Day total | Country
    r+2.. days 1-7            F = =SUM(B{d}:E{d})            G = Country (DROPDOWN)
    r+9   per-category sums   r+10  Total / Grand Total:

This emits:
  writes  — B{d}:E{d+6} numeric block per week, pasted normally
  formatX — restores the currency number format a normal paste flattens
  types   — G column countries, TYPED one cell at a time because the dropdown rejects pastes

Find --first-row by reading the sheet tail in the FORMULA BAR. The gviz CSV export silently
drops rows, so its row numbers do not line up with the real grid.
"""
import argparse
import csv
import json
import os

CATS = ["Food&Drink", "Lodging", "Transportation", "Other"]
# Template lives at Weeks!I180:O190, so its day-row B..E equivalent is J182:M188.
FORMAT_SOURCE = "J182:M188"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", default="sheet-rows.csv")
    ap.add_argument("--first-row", type=int, required=True,
                    help="row of the first macro-created block's 'Week N' cell")
    ap.add_argument("--sheet-url", required=True)
    ap.add_argument("--out", default="payload.json")
    a = ap.parse_args()

    days = list(csv.DictReader(open(a.rows)))
    writes, types, verify = [], [], []

    for wi in range((len(days) + 6) // 7):
        chunk = days[wi * 7:(wi + 1) * 7]
        r = a.first_row + wi * 12
        d0 = r + 2

        rows = []
        for i in range(7):
            c = chunk[i] if i < len(chunk) else None
            rows.append("\t".join(f"{float(c[k]):.2f}" for k in CATS) if c
                        else "\t".join(["0.00"] * 4))
        writes.append({"anchor": f"B{d0}", "tsv": "\n".join(rows)})

        for i in range(7):
            c = chunk[i] if i < len(chunk) else (chunk[-1] if chunk else None)
            if c:
                types.append({"cell": f"G{d0 + i}", "text": c["country"]})

        verify += [f"A{r}", f"B{d0}", f"F{d0}", f"G{d0}", f"E{r + 10}"]

    json.dump({
        "url": a.sheet_url,
        "writes": writes,
        "formatFrom": FORMAT_SOURCE,
        "formatTo": [f"B{a.first_row + wi * 12 + 2}:E{a.first_row + wi * 12 + 8}"
                     for wi in range((len(days) + 6) // 7)],
        "types": types,
        "verify": verify,
    }, open(a.out, "w"), indent=1)

    n = (len(days) + 6) // 7
    print(f"{len(days)} days -> {n} block(s) -> {os.path.abspath(a.out)}")
    print(f"Run the `newweek` macro {n}x first, anchored at:")
    for wi in range(n):
        r = a.first_row + wi * 12
        print(f"  A{r}   (fills rows {r}-{r + 10})")


if __name__ == "__main__":
    main()
