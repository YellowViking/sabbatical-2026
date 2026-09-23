#!/usr/bin/env python3
"""Turn a raw sync-*.json into the day x category grid the Expense sheet wants.

    python3 categorize.py [--sync raw/sync-YYYYMMDD...json] [--start 2026-08-24] [--end 2026-09-13]

Sheet columns are Food&Drink / Lodging / Transportation / Other, one row per day, plus Country.
Amounts are plain USD numbers (the sheet's Currency/rate row is a lookup helper, not a divisor).

Two things this does that a raw CSV export cannot:
  * categorises from the MERCHANT CATEGORY CODE (Chase) or categoryCode (Amex), not merchant-name
    guessing, with a small override table for the cases where the MCC lies (bike share filed under
    7999, food delivery under 4816, hotel bookings under 4722 travel agency);
  * AMORTISES lodging across the nights it covers, which is how the historical sheet is written --
    one 135.37 hotel charge becomes 45.12 on each of three nights, not a spike on the booking date.
"""
import argparse
import collections
import csv
import glob
import json
import os
import sys

FOOD, LODGING, TRANSPORT, OTHER = "Food&Drink", "Lodging", "Transportation", "Other"
CATS = [FOOD, LODGING, TRANSPORT, OTHER]

# ---------------------------------------------------------------- MCC rules --
MCC_RANGES = [
    ((3000, 3299), TRANSPORT),  # airline-specific codes
    ((3500, 3999), LODGING),    # hotel-chain-specific codes
]
MCC = {
    # food & drink
    "5411": FOOD, "5422": FOOD, "5441": FOOD, "5451": FOOD, "5462": FOOD,
    "5499": FOOD, "5811": FOOD, "5812": FOOD, "5813": FOOD, "5814": FOOD,
    "5921": FOOD, "5994": FOOD,  # 5994 = newsagent; here always a 7-Eleven food run
    # lodging
    "7011": LODGING, "7012": LODGING, "4225": LODGING, "4722": LODGING,
    # transport
    "4111": TRANSPORT, "4112": TRANSPORT, "4121": TRANSPORT, "4131": TRANSPORT,
    "4304": TRANSPORT, "4411": TRANSPORT, "4415": TRANSPORT, "4511": TRANSPORT,
    "4582": TRANSPORT, "4784": TRANSPORT, "4789": TRANSPORT, "5541": TRANSPORT,
    "5542": TRANSPORT, "7512": TRANSPORT, "7523": TRANSPORT,
    # other (tickets, tours, museums, shops)
    "5941": OTHER, "5945": OTHER, "5971": OTHER, "7299": OTHER, "7832": OTHER,
    "7911": OTHER, "7922": OTHER, "7991": OTHER, "7996": OTHER, "7998": OTHER,
    "7999": OTHER,
}
AMEX_CAT = {"C7": FOOD, "C8": TRANSPORT, "C9": TRANSPORT, "C3": OTHER, "C5": OTHER}

# Merchant-substring overrides, applied before the MCC. Order matters.
OVERRIDES = [
    ("DONKEY", TRANSPORT),        # Donkey Republic bike share, filed under 7999
    ("FOODORA", FOOD),            # food delivery, filed under 4816
    ("BRITISH AIRWAYS", TRANSPORT),
    ("HOSTELLING INT", LODGING),  # HI membership bought purely to unlock the hostel rate
    ("7-ELEVEN", FOOD),           # Amex files convenience stores as C5 Merchandise
]

# Same merchant, different thing. A hotel or hostel bills incidentals — laundry, a locker, a
# drink — on its own MCC 7011, which would otherwise be read as lodging AND amortised across
# the whole stay. Matching on amount keeps the real room charge intact.
# (merchant substring, exact amount or None, category)
RECLASS = [
    ("City Hostel Stockholm", 15.69, OTHER),   # laundry, not a room charge
]

# Charges that are not trip spend at all.
EXCLUDE = ["LINODE", "UBER ONE", "WALMART", "WAL-MART", "SNAPDOODLE", "RESY CREDIT",
           # Card payments are money moving between your own accounts, not trip spend.
           # Left in, they land as a large negative and quietly cancel out real charges.
           "AUTOPAY PAYMENT", "PAYMENT - THANK YOU", "PAYMENT THANK YOU"]

# Spend the cards never saw (cash, or a card not being synced). Keep it here rather than typing
# it into the sheet by hand, otherwise the next sync silently overwrites it.
# (date, merchant, amount, currency, category)
CASH = [
    ("2026-08-24", "SK938 SEA-CPH award taxes", 5.60, "USD", TRANSPORT),
    ("2026-08-31", "Laundry (Oslo, day 2)", 250, "NOK", OTHER),
    ("2026-09-07", "Museum (Bergen, day 2)", 170, "NOK", OTHER),
]

# Award redemptions. Points are not cash, but leaving them at zero makes a points-funded night
# look free and quietly understates what the trip is worth. Each is valued at CPP cents per
# point and amortised like any other stay/fare.
# (first date, label, points, program, category, nights)
# Each redemption sits on the same day as its own cash fee, so the two read together.
POINTS = [
    ("2026-08-24", "SK938 SEA-CPH (award)", 25500, "VIRGIN", TRANSPORT, 1),
    ("2026-08-27", "Hyatt Place Gothenburg (award)", 7500 * 3, "HYATT", LODGING, 3),
    ("2026-09-08", "AY0806 BGO-ARN (award)", 3250, "AVIOS", TRANSPORT, 1),
    ("2026-09-13", "AY0805 ARN-BGO return (award)", 3250, "AVIOS", TRANSPORT, 1),
]

# Cents per point. Change these in one place to re-value every redemption above.
CPP = {"HYATT": 1.7, "VIRGIN": 1.4, "AVIOS": 1.4, "MR": 1.4, "UR": 1.5}

# Move a charge to the day it actually relates to. Travel is bought ahead of time, so the
# posting date is rarely the day the money "belongs" to: a flight booked on the 10th and flown
# on the 13th reads wrong on both days. Lodging is handled by STAYS; this is for everything else.
# (merchant substring, exact amount or None, real date)
REDATE = [
    ("BRITISH AIRWAYS", 28.10, "2026-09-13"),  # AY0805 ARN->BGO, flown Sun 13 Sep
    ("BRITISH AIRWAYS", 42.70, "2026-09-08"),  # AY0806 BGO->ARN, flown Tue 8 Sep
    ("Norwegian Air Shuttl", 89.05, "2026-09-19"),  # BGO->RIX ref XWH6WP, flown Sat 19 Sep
]

# USD per unit of foreign currency. NOK is derived from a real Chase conversion in this same
# trip window: the HI membership billed 196.02 NOK as $20.30 => 9.6562 NOK/USD.
FX = {"NOK": 9.6562, "SEK": 9.55, "DKK": 6.42, "EUR": 0.91, "USD": 1.0}

# Lodging charges spread across the nights they actually cover.
# (merchant substring, exact amount or None, first night, nights)
# Match on amount, not charge date: the two Booking.com charges landed the same day and are
# otherwise indistinguishable, so a date-only rule silently swaps a 1-night and a 4-night stay.
STAYS = [
    ("MEININGER",      None,   "2026-08-24", 3),   # Copenhagen, checkout Aug 27
    ("Hyatt Place",    None,   "2026-08-27", 3),   # Gothenburg, 3 award nights, checkout Aug 30
    ("COCHS",          None,   "2026-08-30", 2),   # Oslo, checkout Sep 1
    ("BKG*HOTEL",      145.77, "2026-09-01", 1),   # Kristiansand
    ("BKG*HOTEL",      308.07, "2026-09-02", 4),   # Stavanger, Central Guest House
    # Bergen was cut to 2 nights when the Sep 8 BGO->ARN flight was booked: arrived Sep 6,
    # flew out Sep 8 morning. The itinerary's original 6-night Sep 6-12 plan never happened,
    # and the charge agrees -- $123.33 is ~1,191 NOK, about 2 nights of a Montana private
    # twin, not the 2,116 NOK a 6-night stay was quoted at.
    ("MONTANA VANDRE", None,   "2026-09-06", 2),   # Bergen, checkout Sep 8
    ("HOSTELLING INT", None,   "2026-09-06", 2),   # HI card, spread over the nights it unlocked
    # Both Stockholm stays bill through Agoda, so match the PROPERTY, not the OTA. A bare
    # "AGODA" rule would swallow whichever charge it saw first and amortise it over the
    # wrong nights.
    ("CITY HOSTE",     None,   "2026-09-08", 3),   # Stockholm City Hostel, checkout Sep 11
    ("STF STOCKH",     None,   "2026-09-11", 2),   # Stockholm STF Skeppsholmen, checkout Sep 13
]

# Which country each day is spent in. Merchant country is unreliable for the sheet's Country
# column -- Booking.com bills from NL, Agoda from DE, Hostelling International from GB -- so the
# day's country comes from the itinerary. (first date, country) applied until the next entry.
COUNTRY_TIMELINE = [
    ("2026-08-24", "Denmark"),   # land CPH
    ("2026-08-27", "Sweden"),    # Gothenburg
    ("2026-08-30", "Norway"),    # Oslo -> Kristiansand -> Stavanger -> Bergen
    ("2026-09-08", "Sweden"),    # AY0806 BGO->ARN, Stockholm
    ("2026-09-13", "Norway"),    # AY0805 back to Bergen for the fjord road trip
    ("2026-09-20", "Latvia"),    # BGO->RIX lands 22:55 Sat 19 Sep, so Sun 20 is the first Riga day
]

NUMERIC_COUNTRY = {
    "578": "NO", "752": "SE", "208": "DK", "840": "US", "528": "NL",
    "826": "GB", "428": "LV", "276": "DE", "246": "FI", "233": "EE",
}
COUNTRY_NAME = {
    "DK": "Denmark", "SE": "Sweden", "NO": "Norway", "FI": "Finland",
    "EE": "Estonia", "LV": "Latvia", "LT": "Lithuania", "US": "USA",
    "NL": "Netherlands", "GB": "United Kingdom", "DE": "Germany",
}


def complete(path):
    """True if every account in the sync actually returned transactions.

    Bank sessions expire mid-run and both APIs will happily answer 200 with an empty list,
    so a sync file can be silently half-empty. Categorising one of those wipes a whole card
    off the sheet, which looks like a spending drop rather than an error.
    """
    try:
        d = json.load(open(path))
    except Exception:
        return False
    accts = list((d.get("chase") or {}).values())
    accts += [a.get("transactions", []) for a in (d.get("amex") or {}).values()]
    return bool(accts) and all(len(a) for a in accts)


def pick_sync():
    """Newest sync in which no account came back empty."""
    for p in sorted(glob.glob("raw/sync-*.json"), reverse=True):
        if complete(p):
            return p
    return None


def load(sync_path):
    """Flatten both banks into one list of dicts."""
    d = json.load(open(sync_path))
    out = []
    for label, acts in (d.get("chase") or {}).items():
        for a in acts:
            m = (a.get("merchantDetails", {}).get("rawMerchantDetails") or {})
            cc = m.get("merchantCountryCode", "")
            out.append({
                "date": a.get("transactionDate"),
                "card": label,
                "merchant": (m.get("merchantDbaName") or "").strip(),
                "amount": float(a.get("transactionAmount") or 0),
                "mcc": m.get("merchantCategoryCode", ""),
                "country": NUMERIC_COUNTRY.get(cc, cc),
                "pending": a.get("transactionStatusCode") == "Pending",
            })
    for label, acct in (d.get("amex") or {}).items():
        for t in acct.get("transactions", []):
            out.append({
                "date": t["displayDate"],
                "card": label,
                "merchant": t["displayDescription"].strip(),
                "amount": float(t["transactionAmount"]["amount"]),  # already signed
                "mcc": "",
                "amexCat": t.get("categoryCode", ""),
                "country": "",
                "pending": t.get("status") == "pending",
            })
    for r in out:
        for needle, amount, real in REDATE:
            if needle.upper() in r["merchant"].upper() and (amount is None or abs(amount - r["amount"]) < 0.01):
                r["note"] = f"posted {r['date']}, dated to travel day"
                r["date"] = real
                break
    for date, merchant, amt, ccy, cat in CASH:
        out.append({
            "date": date, "card": "cash", "merchant": merchant,
            "amount": round(amt / FX[ccy], 2), "mcc": "", "country": "",
            "pending": False, "forceCat": cat,
            "note": f"cash {amt:g} {ccy}" + ("" if ccy == "USD" else f" @ {FX[ccy]}"),
        })
    import datetime as _dt
    for date, label, pts, prog, cat, nights in POINTS:
        total = pts * CPP[prog] / 100.0
        per = round(total / nights, 2)
        d0 = _dt.date.fromisoformat(date)
        for n in range(nights):
            out.append({
                "date": (d0 + _dt.timedelta(days=n)).isoformat(), "card": "points",
                "merchant": label, "amount": per, "mcc": "", "country": "",
                "pending": False, "forceCat": cat, "preSpread": True,
                "note": f"{pts:,} {prog} @ {CPP[prog]}cpp = ${total:,.2f} / {nights}n",
            })
    return sorted(out, key=lambda r: (r["date"], r["merchant"]))


def classify(r):
    if r.get("forceCat"):
        return r["forceCat"]
    up = r["merchant"].upper()
    for needle, amount, cat in RECLASS:
        if needle.upper() in up and (amount is None or abs(amount - r["amount"]) < 0.01):
            return cat
    for needle, cat in OVERRIDES:
        if needle.upper() in up:
            return cat
    mcc = r.get("mcc") or ""
    if mcc in MCC:
        return MCC[mcc]
    if mcc.isdigit():
        n = int(mcc)
        for (lo, hi), cat in MCC_RANGES:
            if lo <= n <= hi:
                return cat
    if r.get("amexCat") in AMEX_CAT:
        return AMEX_CAT[r["amexCat"]]
    return OTHER


def excluded(r):
    up = r["merchant"].upper()
    return any(x in up for x in EXCLUDE)


def spread(rows):
    """Replace each matched lodging charge with one row per night it covers."""
    import datetime as dt
    out = []
    for r in rows:
        # POINTS rows arrive already split per night; re-amortising them would square the count.
        if classify(r) != LODGING or r.get("preSpread"):
            out.append(r)
            continue
        # Rules are NOT consumed: one property can bill several times for the same stay
        # (Meininger charged three times for the same three nights).
        hit = None
        for needle, amount, first, nights in STAYS:
            if needle.upper() in r["merchant"].upper() and (amount is None or abs(amount - r["amount"]) < 0.01):
                hit = (first, nights)
                break
        if not hit:
            out.append(dict(r, note="lodging, NOT amortised (no STAYS rule)"))
            continue
        first, nights = hit
        per = round(r["amount"] / nights, 2)
        d0 = dt.date.fromisoformat(first)
        for n in range(nights):
            out.append(dict(r, date=(d0 + dt.timedelta(days=n)).isoformat(),
                            amount=per, note=f"amortised {r['amount']:.2f}/{nights}n"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sync")
    ap.add_argument("--start", default="2026-08-24")
    ap.add_argument("--end", default="2026-12-31")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    sync = a.sync or pick_sync()
    if not sync:
        sys.exit("no COMPLETE sync-*.json found (every candidate had an empty account) — "
                 "re-authenticate both banks and run sync.js again")
    newest = (sorted(glob.glob("raw/sync-*.json")) or [None])[-1]
    if a.sync is None and sync != newest:
        print(f"NOTE  newest sync {os.path.basename(newest)} is incomplete (a bank session "
              f"expired mid-run); using {os.path.basename(sync)} instead")

    rows = load(sync)
    kept = [r for r in rows if not excluded(r)]
    dropped = [r for r in rows if excluded(r)]
    kept = spread(kept)
    inrange = [r for r in kept if a.start <= r["date"] <= a.end]

    by_day = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in inrange:
        by_day[r["date"]][classify(r)] += r["amount"]

    def country_for(day):
        cur = ""
        for start, name in COUNTRY_TIMELINE:
            if day >= start:
                cur = name
        return cur

    import datetime as dt
    # Run to --end when it is in the past/near future, so trailing days still get a Country from
    # COUNTRY_TIMELINE instead of inheriting the previous day's. Otherwise stop at the last day
    # that actually has spend.
    # The grid always ends at the last day that HAS a figure. Prepaid lodging amortises into
    # future nights, so --end must stay generous (it is only a filter); ending the grid at
    # "today" would silently drop nights you have already paid for.
    d0 = dt.date.fromisoformat(a.start)
    d1 = max(dt.date.fromisoformat(x) for x in by_day)
    days = []
    while d0 <= d1:
        k = d0.isoformat()
        days.append({"date": k, "country": country_for(k),
                     **{c: round(by_day[k][c], 2) for c in CATS}})
        d0 += dt.timedelta(days=1)

    grid = os.path.join(a.outdir, "sheet-rows.csv")
    with open(grid, "w", newline="") as fh:
        w = csv.DictWriter(fh, ["date"] + CATS + ["country"])
        w.writeheader()
        for r in days:
            w.writerow({"date": r["date"], "country": r["country"], **{c: f"{r[c]:.2f}" for c in CATS}})

    detail = os.path.join(a.outdir, "transactions-classified.csv")
    with open(detail, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "card", "merchant", "amount", "mcc", "country", "category", "pending", "note"])
        for r in sorted(inrange, key=lambda x: (x["date"], x["merchant"])):
            w.writerow([r["date"], r["card"], r["merchant"], f"{r['amount']:.2f}", r.get("mcc", ""),
                        r["country"], classify(r), "Y" if r["pending"] else "", r.get("note", "")])

    print(f"sync      {sync}")
    print(f"excluded  {len(dropped)} non-trip rows: " +
          ", ".join(sorted({r['merchant'][:24] for r in dropped})))
    print(f"wrote     {grid}  ({len(days)} days)")
    print(f"wrote     {detail}  ({len(inrange)} transactions)")
    tot = {c: sum(r[c] for r in days) for c in CATS}
    print("totals    " + "  ".join(f"{c} {tot[c]:.2f}" for c in CATS) +
          f"  ALL {sum(tot.values()):.2f}")


if __name__ == "__main__":
    main()
