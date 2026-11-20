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
import html
import json
import os
import re
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

OVERRIDES = []   # real data: see categorize_private.py (outside the repo)

RECLASS = []   # real data: see categorize_private.py (outside the repo)

SPLIT = []   # real data: see categorize_private.py (outside the repo)

EXCLUDE = []   # real data: see categorize_private.py (outside the repo)

CASH = []   # real data: see categorize_private.py (outside the repo)

POINTS = []   # real data: see categorize_private.py (outside the repo)

# Cents per point. Change these in one place to re-value every redemption above.
CPP = {"HYATT": 1.7, "VIRGIN": 1.4, "AVIOS": 1.4, "MR": 1.4, "UR": 1.5}

REDATE = []   # real data: see categorize_private.py (outside the repo)

SPREAD = []   # real data: see categorize_private.py (outside the repo)

# USD per unit of foreign currency. NOK is derived from a real Chase conversion in this same
# trip window: the HI membership billed 196.02 NOK as $20.30 => 9.6562 NOK/USD.
# EUR from a real Chase conversion too: the Lesce hostel's EUR 22.50 billed as $25.36 (18 Oct).
FX = {"NOK": 9.6562, "SEK": 9.55, "DKK": 6.42, "EUR": 0.8872, "USD": 1.0}

# Settlement rates. A "(my half)" line is not a card charge — it is a USD debt to the person who
# fronted the cost, so it converts at the rate their ledger settles on, NOT at the card's rate.
# The road-trip ledger fixes 1 USD = 9.49 NOK (dated 24 Sep 2026). Using the card rate instead
# understates the shared leg by about $7, because the card rate is the weaker of the two.
SETTLE_FX = {"NOK": 9.49}
SETTLE_MARK = "(my half)"

STAYS = []   # real data: see categorize_private.py (outside the repo)

COUNTRY_TIMELINE = []   # real data: see categorize_private.py (outside the repo)

# Countries that are usually a BILLING address, not where you stood: Booking.com bills NL,
# Hostelworld IE, Agoda DE/US, airlines GB/US. Ignore them on any day that also has a
# real local merchant.
BILLING_ONLY = {"US", "NL", "IE", "GB", "DE", "SG"}   # SG: Agoda/Trip.com $1 card checks
BILLING_MERCHANTS = ()   # real data: see categorize_private.py (outside the repo)

NUMERIC_COUNTRY = {
    "578": "NO", "752": "SE", "208": "DK", "840": "US", "528": "NL",
    "826": "GB", "428": "LV", "276": "DE", "246": "FI", "233": "EE",
    "440": "LT", "616": "PL", "203": "CZ", "040": "AT", "703": "SK", "348": "HU",
    "705": "SI", "191": "HR", "380": "IT", "070": "BA", "499": "ME", "008": "AL", "688": "RS", "702": "SG", "372": "IE",
}
COUNTRY_NAME = {
    "DK": "Denmark", "SE": "Sweden", "NO": "Norway", "FI": "Finland",
    "EE": "Estonia", "LV": "Latvia", "LT": "Lithuania", "US": "USA",
    "NL": "Netherlands", "GB": "United Kingdom", "DE": "Germany",
    "PL": "Poland", "CZ": "Czechia", "AT": "Austria", "SK": "Slovakia", "HU": "Hungary",
    "SI": "Slovenia", "HR": "Croatia", "IT": "Italy", "BA": "Bosnia and Herzegovina",
    "ME": "Montenegro", "AL": "Albania", "RS": "Serbia",
}


# Chase's own category labels, used only for CSV-sourced rows (the JSON feed has real MCCs).
# "Travel" is ambiguous — it covers both a hotel and a bus ticket — so lodging is detected by
# merchant name and everything else in Travel falls to Transportation.
CSV_CATEGORY = {
    "Groceries": FOOD, "Food & Drink": FOOD, "Gas": TRANSPORT, "Automotive": TRANSPORT,
    "Shopping": OTHER, "Entertainment": OTHER, "Home": OTHER, "Personal": OTHER,
    "Health & Wellness": OTHER, "Bills & Utilities": OTHER, "Fees & Adjustments": OTHER,
    "Travel": TRANSPORT,   # lodging inside "Travel" is caught by LODGING_NAME first
}
LODGING_NAME = re.compile(
    r"HOTEL|HOSTEL|BKG\*|AGODA|BOOKING\.C|VANDRE|PENSJONAT|GUEST\s?HOUSE|CAMPING|B&B|SOBE|APARTMA", re.I)


def load_chase_csv(path):
    """Chase's download CSV — the only way to reach a CLOSED statement cycle.

    The JSON transactions endpoint is hard-scoped to the current cycle: once a statement closes,
    everything older vanishes from it and no date parameter brings it back. Without this the
    sheet silently loses whole weeks. Amounts are negative for purchases here, and the file
    carries HTML entities.
    """
    out = []
    for r in csv.DictReader(open(path)):
        if (r.get("Type") or "").lower() == "payment":
            continue
        amt = float(r["Amount"])           # purchases negative; refunds/credits positive and KEPT
        if amt == 0:
            continue
        name = html.unescape(r["Description"]).strip()
        cat = LODGING_NAME.search(name) and LODGING or CSV_CATEGORY.get(r.get("Category", ""), OTHER)
        m, d, y = r["Transaction Date"].split("/")
        out.append({
            "date": f"{y}-{m}-{d}", "card": "Sapphire Preferred (csv)", "merchant": name,
            "amount": round(-amt, 2), "mcc": "", "country": "", "pending": False,
            "csvCat": cat, "note": "from statement CSV",
        })
    return out


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


def build_ledger():
    """Union of EVERY complete sync, plus any statement CSVs, deduped.

    A single sync is not a full history. Chase's JSON endpoint only returns the current
    statement cycle, so the newest pull alone would drop every earlier week. Merging across all
    pulls keeps what previous ones saw; the CSVs fill cycles that closed between pulls.

    Dedup key is (date, merchant, amount) rather than the bank's transaction id: a pending row
    and its posted twin get different ids, and the CSV has no id at all. Genuine same-day
    duplicates (two identical coffees) are preserved by counting occurrences per source and
    keeping the highest count seen.
    """
    rows, seen_counts = [], collections.Counter()

    def key(r):
        return (r["date"], r["merchant"].strip().upper(), round(r["amount"], 2))

    for path in sorted(glob.glob("raw/sync-*.json")):
        if not complete(path):
            continue
        batch = load(path)
        counts = collections.Counter(key(r) for r in batch)
        for k, n in counts.items():
            if n > seen_counts[k]:
                extra = [r for r in batch if key(r) == k][seen_counts[k]:n]
                rows.extend(extra)
                seen_counts[k] = n

    # Between pulls a charge moves Pending -> Posted and Chase rewrites BOTH the date and the
    # merchant name: "SKYSS" -> "SKYSS APP", "BRITISH AIRWAYS US DIRECT ECOM" -> "... US DUSA",
    # Agoda pending Sep 9 -> posted Sep 10. Exact-key dedup therefore keeps both and every such
    # charge is counted twice. Reconcile on a short merchant prefix + amount + nearby date.
    import datetime as _dt

    def norm(m):
        return re.sub(r"[^A-Z0-9]", "", m.upper())

    def same_merchant(a, b):
        # A fixed-length stem fails when the rename only appends ("SKYSS" -> "SKYSS APP" gives
        # stems SKYSS vs SKYSSA). Compare how much of the two names actually agree instead.
        n = 0
        for x, y in zip(a, b):
            if x != y:
                break
            n += 1
        return n >= 5 and n >= min(len(a), len(b)) - 12

    posted = collections.defaultdict(list)
    for r in rows:
        if not r.get("pending"):
            posted[round(r["amount"], 2)].append((norm(r["merchant"]), r["date"]))

    deduped = []
    for r in rows:
        if r.get("pending"):
            me = norm(r["merchant"])
            # NB: the posted twin is often on the SAME date with only the name rewritten, so do
            # not require the dates to differ — that was letting every same-day pair through.
            if any(same_merchant(me, pm)
                   and abs((_dt.date.fromisoformat(pd) - _dt.date.fromisoformat(r["date"])).days) <= 5
                   for pm, pd in posted.get(round(r["amount"], 2), [])):
                continue
        deduped.append(r)
    rows = deduped

    # Statement CSVs exist ONLY to fill cycles the JSON never covered. Chase's CSV description
    # differs from the JSON merchant name ("CITY HOSTEL" vs "City Hostel Stockholm AB"), so
    # cross-source matching double-counts. Restrict CSVs to dates no JSON pull reached.
    # CSV rows are matched to Chase JSON rows ONE-FOR-ONE on (date, amount); only the CSV rows
    # left over are added. Matching on whole DAYS was wrong twice over: a statement boundary
    # splits a day between the closed cycle (CSV) and the new one (JSON), and a single stray
    # pending $1 dated Oct 16 made that whole day "covered" -- silently dropping the Agoda
    # prepayment and both train tickets. Names can't be matched: the CSV says "CITY HOSTEL"
    # where the JSON says "City Hostel Stockholm AB".
    import datetime as dt
    unmatched = collections.Counter((r["date"], round(r["amount"], 2)) for r in rows if r.get("bank") == "chase")
    pend = [r for r in rows if r.get("bank") == "chase" and r.get("pending")]
    # Statement CSVs overlap each other (every sync saves a rolling ~75-day export), so each
    # date is taken from ONE file only — the newest, which also has the most complete last day.
    claimed = set()
    for path in sorted(glob.glob("raw/csv/*.csv"), key=os.path.getmtime, reverse=True):
        got = load_chase_csv(path)
        for r in got:
            if r["date"] in claimed:
                continue
            k = (r["date"], round(r["amount"], 2))
            if unmatched[k] > 0:
                unmatched[k] -= 1
                continue
            # A PENDING JSON row can carry a different date from the posted charge (Lime 0.52:
            # pending Oct 8, posted Oct 10). Same amount within 5 days of a still-unmatched
            # pending row = the same charge.
            d0 = dt.date.fromisoformat(r["date"])
            stem = lambda x: re.sub(r"[^A-Z0-9]", "", x.upper())[:4]
            twin = next((p for p in pend if abs(p["amount"] - r["amount"]) < 0.01
                         and stem(p["merchant"]) == stem(r["merchant"])   # Lime/LIME, not KA BLED/1A
                         and abs((dt.date.fromisoformat(p["date"]) - d0).days) <= 5
                         and unmatched[(p["date"], round(p["amount"], 2))] > 0), None)
            if twin:
                unmatched[(twin["date"], round(twin["amount"], 2))] -= 1
                continue
            rows.append(r)
        claimed |= {r["date"] for r in got}

    return rows


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
                "bank": "chase",
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
    return out


def finalize(out):
    """Apply SPLIT/REDATE to bank rows, then append CASH and POINTS.

    Runs ONCE on the merged ledger — doing it per-sync would re-split a shared charge every
    time it reappeared in a later pull.
    """
    for r in out:
        for needle, amount, share in SPLIT:
            if needle.upper() in r["merchant"].upper() and (amount is None or abs(amount - r["amount"]) < 0.01):
                full = r["amount"]
                r["amount"] = round(full * share, 2)
                r["note"] = f"split {share:.0%} of {full:.2f}"
                break
    for r in out:
        for needle, amount, real in REDATE:
            if needle.upper() in r["merchant"].upper() and (amount is None or abs(amount - r["amount"]) < 0.01):
                r["note"] = f"posted {r['date']}, dated to travel day"
                r["date"] = real
                break
    for date, merchant, amt, ccy, cat in CASH:
        rate = SETTLE_FX.get(ccy, FX[ccy]) if SETTLE_MARK in merchant else FX[ccy]
        out.append({
            "date": date, "card": "cash", "merchant": merchant,
            "amount": round(amt / rate, 2), "mcc": "", "country": "",
            "pending": False, "forceCat": cat,
            "note": f"cash {amt:g} {ccy}" + ("" if ccy == "USD" else f" @ {rate}"),
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
    for needle, cat in OVERRIDES:      # before csvCat: Chase files FlixBus under "Other"
        if needle.upper() in up:
            return cat
    if r.get("csvCat"):          # CSV rows carry no MCC; trust Chase's own label
        return r["csvCat"]
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


HOLDS = []   # real data: see categorize_private.py (outside the repo)


MANUAL_GUARD = []   # real data: see categorize_private.py (outside the repo)


def excluded(r):
    up = r["merchant"].upper()
    if r.get("card") != "cash" and any(abs(r["amount"] - a) < 0.01 and lo <= r["date"] <= hi
                                       for a, lo, hi in MANUAL_GUARD):
        return True
    if r.get("pending") and any(n.upper() in up and abs(a - r["amount"]) < 0.01 for n, a in HOLDS):
        return True
    return any(x in up for x in EXCLUDE)


def spread(rows):
    """Replace each matched charge with one row per day it covers.

    Two tables feed this: SPREAD for anything (passes, packaged ride-hail bills) and STAYS for
    lodging nights. SPREAD is checked first so a transport pass is not skipped just because it
    is not lodging.
    """
    import datetime as dt
    out = []
    for r in rows:
        if r.get("preSpread"):
            out.append(r)
            continue

        hit = None
        for needle, amount, first, days in SPREAD:
            if needle.upper() in r["merchant"].upper() and (amount is None or abs(amount - r["amount"]) < 0.01):
                hit = (first, days)
                break
        if hit:
            first, days = hit
            per = round(r["amount"] / days, 2)
            d0 = dt.date.fromisoformat(first)
            for n in range(days):
                out.append(dict(r, date=(d0 + dt.timedelta(days=n)).isoformat(),
                                amount=per, preSpread=True,
                                note=f"spread {r['amount']:.2f}/{days}d"))
            continue

        # POINTS rows arrive already split per night; re-amortising them would square the count.
        if classify(r) != LODGING:
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
    ap.add_argument("--start", default="2026-08-23")
    ap.add_argument("--end", default="2026-12-31")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    if a.sync:
        rows = finalize(load(a.sync))
        print(f"sync      {a.sync} (single file, --sync given)")
    else:
        ledger = build_ledger()
        if not ledger:
            sys.exit("no COMPLETE sync-*.json found — re-authenticate both banks and re-run")
        rows = finalize(ledger)
        syncs = [p for p in sorted(glob.glob("raw/sync-*.json")) if complete(p)]
        csvs = sorted(glob.glob("raw/csv/*.csv"))
        print(f"ledger    {len(syncs)} sync(s) + {len(csvs)} statement CSV(s) -> {len(ledger)} rows")
    kept = [r for r in rows if not excluded(r)]
    dropped = [r for r in rows if excluded(r)]
    kept = spread(kept)
    inrange = [r for r in kept if a.start <= r["date"] <= a.end]

    by_day = collections.defaultdict(lambda: collections.defaultdict(float))
    for r in inrange:
        by_day[r["date"]][classify(r)] += r["amount"]

    # Where you actually were, from the MERCHANT GEO on each day's card charges. A hand-written
    # timeline goes stale the moment plans change — it had Latvia for a week spent in Finland,
    # because it was built from a booked flight rather than from where money was being spent.
    geo = collections.defaultdict(collections.Counter)
    for r in inrange:
        if r.get("country") and not r["merchant"].upper().startswith(BILLING_MERCHANTS):
            geo[r["date"]][r["country"]] += 1

    def observed(day):
        c = geo.get(day)
        if not c:
            return None
        local = {k: v for k, v in c.items() if k not in BILLING_ONLY}
        if not local:            # only billing addresses (Booking NL, a $1 SG card check): no signal
            return None
        pick = local
        return COUNTRY_NAME.get(max(pick, key=pick.get), max(pick, key=pick.get))

    def country_for(day, _last=[""]):
        manual = ""
        for start, name in COUNTRY_TIMELINE:      # explicit override wins if set for this day
            if day == start:
                manual = name
        got = manual or observed(day) or _last[0]
        if got:
            _last[0] = got
        return got

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

    print(f"excluded  {len(dropped)} non-trip rows: " +
          ", ".join(sorted({r['merchant'][:24] for r in dropped})))
    print(f"wrote     {grid}  ({len(days)} days)")
    print(f"wrote     {detail}  ({len(inrange)} transactions)")
    tot = {c: sum(r[c] for r in days) for c in CATS}
    print("totals    " + "  ".join(f"{c} {tot[c]:.2f}" for c in CATS) +
          f"  ALL {sum(tot.values()):.2f}")


# Personal tables (merchants, amounts, stays, splits) are kept out of this public repo.
# Point EXPENSE_PRIVATE at the file, default ~/Documents/sabbatical-finance/categorize_private.py.
_PRIVATE = os.path.expanduser(os.environ.get("EXPENSE_PRIVATE", "~/Documents/sabbatical-finance/categorize_private.py"))
if os.path.exists(_PRIVATE):
    exec(compile(open(_PRIVATE).read(), _PRIVATE, "exec"), globals())
else:
    print(f"note: {_PRIVATE} not found; running without personal overrides", file=sys.stderr)


if __name__ == "__main__":
    main()
