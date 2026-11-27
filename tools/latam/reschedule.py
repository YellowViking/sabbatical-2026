#!/usr/bin/env python3
"""Reschedule the LatAm v5 plan from trips/latam/schedule.json, in TRIP DAYS.

Since 27 Nov 2026 the guides, itinerary, alternatives and budget show no calendar dates for the plan: every plan day
is a trip day, "Day 41" (Day 1 = `start` in schedule.json = arrival in Rio; Day 0 = the flight there). Ranges read
"Day 41 → 45" (arrive → leave) or "Days 41–45". Only three kinds of real date stay in the text:
  * fixed-calendar facts (Christmas, Carnaval, holidays, festivals, a race, the full moon, spring breaks);
  * check dates ("✅ 27 Nov", "checked 26 Nov"), which lie outside the trip window;
  * booking-link dates inside URLs (YYYY-MM-DD, DD-MM-YYYY, Google Flights tfs=), so every link stays one click.

Moving the trip:
  * Whole trip later or earlier: change `start` (and `trip_day_1`) in schedule.json and run --apply. No text changes;
    only the booking links move.
  * One stay longer or shorter: change its `nights`, then run --apply. Later trip days are renumbered in every file,
    day-table rows get their holiday tags recomputed from fixed_events, and links move.

  python3 tools/latam/reschedule.py              # dry run: the calendar, per-stay shifts, what would change
  python3 tools/latam/reschedule.py --apply      # rewrite the files, update schedule.lock.json, redraw both maps
  python3 tools/latam/reschedule.py --to-relative [--apply]   # one-off: turn calendar dates in the text into trip days

After a shift, re-check the lines it prints: weekday-only services and closures may now fall on other days.
"""
import argparse, base64, datetime as dt, glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LATAM = os.path.join(ROOT, 'trips', 'latam'); GUIDES = os.path.join(LATAM, 'guides')
SCHED = os.path.join(LATAM, 'schedule.json'); LOCK = os.path.join(LATAM, 'schedule.lock.json')
FILES = lambda: sorted(glob.glob(os.path.join(GUIDES, '*.md'))) + [os.path.join(LATAM, f) for f in ('itinerary.md', 'alternatives.md', 'budget-forecast.md')]
MON = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Dec': 12}; MNAME = {v: k for k, v in MON.items()}
WD = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
D = dt.date; TD = dt.timedelta
WDR = r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)'; MR = r'(?:Dec|Jan|Feb|Mar)'
# lines about fixed-calendar events keep their real dates (only their trip-day tokens move)
EVENT = re.compile(r'Christmas|Navidad|Nochebuena|New Year|Réveillon|Año Nuevo|Carnaval|Carnival|Candelaria|Alasitas|'
                   r'Día del|holiday|feriado|Semana Santa|spring.break|March break|full moon|moon|Carrera|race|festival|'
                   r'Tilcareño|Natal Luz|exodus', re.I)
TAG_DROP = re.compile(r'^(?:.*(?:Christmas|New Year|Carnaval|Día del Estado|Alasitas).*)$')

def year_for(m): return 2026 if m == 12 else 2027
def fmt(d): return f'{WD[d.weekday()]} {d.day} {MNAME[d.month]}'
def parse_dm(day, mon, yr=None):
    m = MON[mon]; return D(int(yr) if yr else year_for(m), m, int(day))

def compute(S):
    d = D.fromisoformat(S['start']); stays = []
    for s in S['stays']:
        stays.append(dict(s, arr=d, dep=d + TD(days=s['nights']))); d += TD(days=s['nights'])
    return stays

def mapper(old_stays, new_stays):
    """old calendar date → new calendar date, following the stay each date belongs to"""
    new_by = {s['id']: s for s in new_stays}
    start_old, end_old = old_stays[0]['arr'], old_stays[-1]['dep']
    start_new, end_new = new_stays[0]['arr'], new_stays[-1]['dep']
    def m(d):
        if d < start_old - TD(days=1) or d > end_old + TD(days=2): return d          # outside the trip: a fixed date
        if d < start_old: return start_new - (start_old - d)
        if d >= end_old: return end_new + (d - end_old)
        for i, s in enumerate(old_stays):
            if s['arr'] <= d < s['dep']:
                n = new_by.get(s['id'])
                if not n:
                    for t in old_stays[i + 1:]:
                        if t['id'] in new_by: return new_by[t['id']]['arr']
                    return end_new
                return n['arr'] + TD(days=min((d - s['arr']).days, max(n['nights'] - 1, 0)))
        return d
    return m

# ---------- booking links: real dates inside URLs ----------
ISO = re.compile(r'\b(2026-1[12]-\d\d|2027-0[1-3]-\d\d)\b'); DMY = re.compile(r'\b(\d\d)-(\d\d)-(2026|2027)\b')
TFS = re.compile(r'tfs=([A-Za-z0-9_-]+)')
def map_urls(s, f):
    s = ISO.sub(lambda mm: f(D.fromisoformat(mm.group(1))).isoformat(), s)
    s = DMY.sub(lambda mm: (lambda n: f'{n.day:02d}-{n.month:02d}-{n.year}')(f(D(int(mm.group(3)), int(mm.group(2)), int(mm.group(1))))), s)
    def tfs(mm):
        raw = mm.group(1); pad = '=' * (-len(raw) % 4)
        try: b = base64.urlsafe_b64decode(raw + pad)
        except Exception: return mm.group(0)
        b2 = re.sub(rb'(2026-1[12]-\d\d|2027-0[1-3]-\d\d)', lambda x: f(D.fromisoformat(x.group(1).decode())).isoformat().encode(), b)
        return 'tfs=' + base64.urlsafe_b64encode(b2).decode().rstrip('=')
    return TFS.sub(tfs, s)

# ---------- trip-day tokens ----------
DAYTOK = re.compile(r'\b(?P<w>Days?) (?P<a>\d{1,3})(?:(?P<sep> → |–)(?P<b>\d{1,3}))?\b(?! of the)')
DAYROW = re.compile(r'^\| \*\*Day (?P<n>\d{1,3})\*\*(?P<tags>(?: · [^|]*)?)\|(?P<rest>.*)$')

def map_days(s, g):
    def rep(mm):
        a = g(int(mm.group('a')))
        if mm.group('b') is None: return f"{mm.group('w')} {a}"
        return f"{mm.group('w')} {a}{mm.group('sep')}{g(int(mm.group('b')))}"
    return DAYTOK.sub(rep, s)

def day_row(n, tags, rest, date, events):
    keep = [x.strip() for x in tags.split(' · ') if x.strip() and not TAG_DROP.match(x.strip())]
    ev = [e['label'] for e in events if e['date'] == date.isoformat()]
    return f"| **Day {n}**{''.join(' · ' + x for x in keep + ev)} |{rest}"

# ---------- one-off conversion: calendar dates in the text → trip days ----------
_D1 = rf'(?:(?P<wd1>{WDR}) )?(?P<d1>\d{{1,2}})(?: (?P<m1>{MR}))?(?: (?P<y1>2026|2027))?'
_D2 = rf'(?:(?P<wd2>{WDR}) )?(?P<d2>\d{{1,2}}) (?P<m2>{MR})\b(?: (?P<y2>2026|2027))?'
R_ARROW = re.compile(rf'\b{_D1} → {_D2}')
R_DASH = re.compile(rf'\b{_D1} ?[–-] ?{_D2}')
R_ONE = re.compile(rf'\b(?:(?P<wd>{WDR}) )?(?P<d>\d{{1,2}}) (?P<m>{MR})\b(?: (?P<y>2026|2027))?')
URLSPAN = re.compile(r'\]\([^)]*\)|(?:href|src)="[^"]*"|https?://\S+')

def _safe(fn):
    def w(mm):
        try: return fn(mm)
        except (ValueError, KeyError): return mm.group(0)
    return w

def to_rel_text(s, T, inwin):
    def two(mm):
        d2 = parse_dm(mm.group('d2'), mm.group('m2'), mm.group('y2'))
        d1 = parse_dm(mm.group('d1'), mm.group('m1') or mm.group('m2'), mm.group('y1') or (mm.group('y2') if not mm.group('m1') else None))
        if not mm.group('m1') and d1 > d2:
            pm = (d2.month - 2) % 12 + 1
            if pm not in MNAME: return None, None
            d1 = parse_dm(mm.group('d1'), MNAME[pm])
        return d1, d2
    def arrow(mm):
        d1, d2 = two(mm)
        return f'Day {T(d1)} → {T(d2)}' if d1 and inwin(d1) and inwin(d2) else mm.group(0)
    def dash(mm):
        d1, d2 = two(mm)
        return f'Days {T(d1)}–{T(d2)}' if d1 and inwin(d1) and inwin(d2) else mm.group(0)
    def one(mm):
        d = parse_dm(mm.group('d'), mm.group('m'), mm.group('y'))
        return f'Day {T(d)}' if inwin(d) else mm.group(0)
    arrow, dash, one = _safe(arrow), _safe(dash), _safe(one)
    out, last = [], 0
    for u in URLSPAN.finditer(s):           # never touch link targets
        seg = s[last:u.start()]; out.append(R_ONE.sub(one, R_DASH.sub(dash, R_ARROW.sub(arrow, seg)))); out.append(u.group(0)); last = u.end()
    seg = s[last:]; out.append(R_ONE.sub(one, R_DASH.sub(dash, R_ARROW.sub(arrow, seg))))
    return ''.join(out)

_WDD = rf'(?P<wd>{WDR}) (?P<d>\d{{1,2}})\b(?! (?:Dec|Jan|Feb|Mar|Nov))(?!:|\d| ?h\b| ?min| ?km)'
R_WD_ARROW = re.compile(rf'\b(?P<wa>{WDR}) (?P<da>\d{{1,2}}) → (?P<wb>{WDR}) (?P<db>\d{{1,2}})\b(?! (?:Dec|Jan|Feb|Mar|Nov))')
R_WD_ONE = re.compile(rf'\b{_WDD}')

def wd_pass(line, T, window):
    """'Mon 4', 'Mon 4 → Wed 6' with no month: resolve inside the guide's own window (unique weekday + day only)"""
    def find(wd, d):
        hits = [x for x in window if x.day == int(d) and WD[x.weekday()] == wd]
        return hits[0] if len(hits) == 1 else None
    def arrow(mm):
        a, b = find(mm.group('wa'), mm.group('da')), find(mm.group('wb'), mm.group('db'))
        return f'Day {T(a)} → {T(b)}' if a and b else mm.group(0)
    def one(mm):
        a = find(mm.group('wd'), mm.group('d'))
        return f'Day {T(a)}' if a else mm.group(0)
    out, last = [], 0
    for u in URLSPAN.finditer(line):
        seg = line[last:u.start()]; out.append(R_WD_ONE.sub(one, R_WD_ARROW.sub(arrow, seg))); out.append(u.group(0)); last = u.end()
    out.append(R_WD_ONE.sub(one, R_WD_ARROW.sub(arrow, line[last:])))
    return ''.join(out)

def to_relative(text, T, inwin, events, window=()):
    out = []
    for line in text.split('\n'):
        m = re.match(rf'^\| \*\*(?:(?P<lab>[^*|]+?) · )?Day (?P<n>\d+)\*\* · (?P<date>{WDR} \d{{1,2}} {MR})(?P<tags>[^|]*)\|(?P<rest>.*)$', line)
        if m:                                                  # day-table row: per-stop "Day n · date" → trip day
            d = parse_dm(*m.group('date').split()[1:])
            line = day_row(T(d), m.group('tags'), m.group('rest'), d, events)
            out.append(line); continue
        # dated markers "Day n (Ddd D Mon)" → trip day
        line = re.sub(rf'(?:(?P<lab>[A-Z][\w ]+?) · )?Day \d+ \((?P<date>{WDR} \d{{1,2}} {MR})\)',
                      lambda mm: f"Day {T(parse_dm(*mm.group('date').split()[1:]))}", line)
        if line.startswith('> **') or line.startswith('#') or not EVENT.search(line):
            line = to_rel_text(line, T, inwin)
            if window: line = wd_pass(line, T, window)
        line = re.sub(r' ?\(days \d+–\d+\)', '', line)                         # old "(days a–b)" in stop headers
        line = re.sub(r'\bDay (\d+) · Day \1\b', r'Day \1', line)               # "Day 25 · Day 25"
        line = re.sub(r'\bDay (\d+) \(Day \1\)', r'Day \1', line)               # "Day 52 (Day 52)"
        out.append(line)
    return '\n'.join(out)

WEEKDAY_SENSITIVE = re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?:day)?s? only|Mon–Fri|Mon–Sat|Tue–Sun|Wed–Sun|weekdays|weekend|'
                               r'Sundays?|Saturdays?|\b(?:Wed|Sat)/(?:Wed|Sat)\b|closed (?:on )?(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)|no Sunday|no bus Sat', re.I)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true'); ap.add_argument('--to-relative', action='store_true')
    a = ap.parse_args()
    S = json.load(open(SCHED)); new_stays = compute(S); events = S.get('fixed_events', [])
    start_new = D.fromisoformat(S.get('trip_day_1', S['start']))
    end_new = new_stays[-1]['dep']
    Tn = lambda d: (d - start_new).days + 1
    print(f"Trip: Day 1 = {fmt(start_new)} {start_new.year} → home on Day {Tn(end_new)} ({fmt(end_new)}), {(end_new - new_stays[0]['arr']).days} nights")

    if a.to_relative:
        inwin = lambda d: start_new - TD(days=1) <= d <= end_new + TD(days=1)
        trip = [start_new + TD(days=i) for i in range(-1, (end_new - start_new).days + 2)]
        for p in FILES():
            gname = os.path.basename(p)[:-3]
            mine = [s for s in new_stays if s['guide'] == gname]
            if mine:   # the guide's own stays, a week either side
                lo, hi = mine[0]['arr'] - TD(days=7), mine[-1]['dep'] + TD(days=7)
                window = [d for d in trip if lo <= d <= hi]
            else:
                window = trip
            old = open(p).read(); new = to_relative(old, Tn, inwin, events, window)
            if new != old:
                n = sum(1 for x, y in zip(old.split('\n'), new.split('\n')) if x != y)
                print(f'  {os.path.relpath(p, LATAM)}: {n} lines → trip days')
                if a.apply: open(p, 'w').write(new)
        print('\nApplied.' if a.apply else '\nDry run. Add --apply to write.'); return

    L = json.load(open(LOCK)) if os.path.exists(LOCK) else {'start': S['start'], 'stays': S['stays']}
    old_S = dict(S, start=L['start'], stays=L['stays']); old_stays = compute(old_S)
    start_old = D.fromisoformat(L.get('trip_day_1', L['start']))
    f = mapper(old_stays, new_stays)
    g = lambda t: Tn(f(start_old + TD(days=t - 1)))            # old trip day → new trip day
    old_by = {s['id']: s for s in old_stays}; shifts = {}
    for s in new_stays:
        o = old_by.get(s['id']); delta = (Tn(s['arr']) - ((o['arr'] - start_old).days + 1)) if o else None
        flag = '' if delta == 0 else (f'  shift {delta:+d} d' if delta is not None else '  NEW')
        ev = [e['label'] for e in events if s['arr'] <= D.fromisoformat(e['date']) < max(s['dep'], s['arr'] + TD(days=1))]
        print(f"  Day {Tn(s['arr']):>2} → {Tn(s['dep']):>2}  ({fmt(s['arr'])} → {fmt(s['dep'])})  {s['nights']} n  {s['id']:22} {s.get('kind','')}{flag}{'  ⚑ ' + ', '.join(sorted(set(ev))) if ev else ''}")
        shifts[s['guide']] = shifts.get(s['guide']) or (delta not in (0, None))
    opt = {o['guide']: o for o in S.get('optional', [])}
    report = []
    for p in FILES():
        gname = os.path.basename(p)[:-3]; ff, gg = f, g
        if gname in opt:   # optional guides move with their anchor
            anc = opt[gname]['anchor']; nd = next(s for s in new_stays if s['id'] == anc)['arr'] - old_by[anc]['arr']
            ff = (lambda dlt: (lambda d: d + dlt if D(2026, 12, 1) <= d <= D(2027, 3, 31) else d))(nd)
            gg = lambda t, ff=ff: Tn(ff(start_old + TD(days=t - 1)))
        old = open(p).read(); out = []
        for line in old.split('\n'):
            m = DAYROW.match(line)
            if m:
                n = gg(int(m.group('n'))); line = day_row(n, m.group('tags'), m.group('rest'), start_new + TD(days=n - 1), events)
            else:
                line = map_days(line, gg)
            out.append(map_urls(line, ff))
        new = '\n'.join(out)
        if new != old:
            n = sum(1 for x, y in zip(old.split('\n'), new.split('\n')) if x != y)
            print(f'  {os.path.relpath(p, LATAM)}: {n} lines change')
            if a.apply: open(p, 'w').write(new)
        if shifts.get(gname) or gname in opt:
            for i, l in enumerate(new.split('\n')):
                if WEEKDAY_SENSITIVE.search(l): report.append(f'{gname}.md:{i+1}: {l.strip()[:150]}')
    if report and any(shifts.values()):
        print('\nRe-check these (weekday-only services, closures, events) in the guides that moved:')
        for r in report[:200]: print('  ' + r)
    if a.apply:
        json.dump({'start': S['start'], 'trip_day_1': S.get('trip_day_1', S['start']), 'stays': S['stays']}, open(LOCK, 'w'), ensure_ascii=False, indent=1)
        geo = os.environ.get('GEO', '/tmp/countries.geojson')   # redraw the route + alternatives maps
        if os.path.exists(geo):
            import subprocess
            for scr, out_ in (('latam_plan_map.py', 'latam-route-draft.svg'), ('latam_alt_map.py', 'latam-alternatives-map.svg')):
                subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'route-map', scr), geo, os.path.join(LATAM, out_)], check=False)
        else:
            print('Maps not redrawn: download the countries file first (see tools/route-map/latam_plan_map.py), or set GEO=…')
        print('\nApplied; schedule.lock.json updated.')
    else:
        print('\nDry run. Add --apply to write.')

if __name__ == '__main__':
    main()
