#!/usr/bin/env python3
"""Reschedule the LatAm v5 guides from trips/latam/schedule.json.

The schedule holds the start date and every stay's nights (night buses and sub-stays included). Guides use relative
day labels ("**Day 2** · Thu 21 Jan" in day tables, "**Day 1 (Sat 30 Jan), Chivay:**" in prose); this script fills the
calendar dates in from the schedule, so moving a stop is: edit nights in schedule.json, then

  python3 tools/latam/reschedule.py            # dry run: calendar, per-stop shifts, what would change
  python3 tools/latam/reschedule.py --apply    # rewrite the guides + itinerary tables, update schedule.lock.json

What moves: day-table dates and their holiday tags (recomputed from fixed_events), "Day N (date)" markers, summary-line
ranges and "(days a–b)", headings, table cells (Book/Transport "When" columns), weekday-dated prose outside sentences
about fixed events, and booking-link dates (YYYY-MM-DD, DD-MM-YYYY, Google Flights tfs=). Fixed-calendar facts
(Carnaval, holidays, full moon, "checked 24 Nov", "since 3 Aug") are never moved. After a shift, re-check the lines it
prints: weekday-only services, closures and events that now fall on different days.
"""
import argparse, base64, datetime as dt, glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LATAM = os.path.join(ROOT, 'trips', 'latam'); GUIDES = os.path.join(LATAM, 'guides')
SCHED = os.path.join(LATAM, 'schedule.json'); LOCK = os.path.join(LATAM, 'schedule.lock.json')
MON = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Dec': 12}; MNAME = {v: k for k, v in MON.items()}
WD = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
D = dt.date; TD = dt.timedelta
WDR = r'(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)'; MR = r'(?:Dec|Jan|Feb|Mar)'
FIXED_KW = re.compile(r'Carnaval|Candelaria|holiday|Día del|Alasitas|moon|festival|Christmas|Nochebuena|New Year|Réveillon|'
                      r'since|updated|checked|listed|valid|as of|reported|until further|closed on|\bon \d{1,2} Nov', re.I)
REGION = {'argentina', 'brazil', 'chile-bolivia', 'costa-rica-nicaragua', 'paraguay-uruguay', 'peru-panama'}

def year_for(m): return 2026 if m == 12 else 2027
def fmt(d, wd=True, year=False): return (f'{WD[d.weekday()]} ' if wd else '') + f'{d.day} {MNAME[d.month]}' + (f' {d.year}' if year else '')

def compute(S):
    d = D.fromisoformat(S['start']); stays = []
    for s in S['stays']:
        stays.append(dict(s, arr=d, dep=d + TD(days=s['nights']))); d += TD(days=s['nights'])
    blocks = {}  # guide -> list of [label, start, end]; contiguous stays of one guide form a block
    for s in stays:
        b = blocks.setdefault(s['guide'], [])
        if b and b[-1][2] == s['arr'] and b[-1][0] == s.get('label'): b[-1][2] = s['dep']
        else: b.append([s.get('label'), s['arr'], s['dep']])
    return stays, blocks

def mapper(old_stays, new_stays):
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
                if not n:  # stay removed: map to the next stay that still exists
                    for t in old_stays[i + 1:]:
                        if t['id'] in new_by: return new_by[t['id']]['arr']
                    return end_new
                off = (d - s['arr']).days
                return n['arr'] + TD(days=min(off, max(n['nights'] - 1, 0)))
        return d
    return m

def parse_dm(day, mon, yr=None):
    m = MON[mon]; return D(int(yr) if yr else year_for(m), m, int(day))

SINGLE = re.compile(rf'\b(?:(?P<wd>{WDR}) )?(?P<d>\d{{1,2}}) (?P<m>{MR})\b(?: (?P<y>2026|2027))?')
RANGE = re.compile(rf'\b(?:(?P<wd1>{WDR}) )?(?P<d1>\d{{1,2}})(?: (?P<m1>{MR}))?(?: (?P<y1>2026|2027))? → (?:(?P<wd2>{WDR}) )?(?P<d2>\d{{1,2}}) (?P<m2>{MR})\b(?: (?P<y2>2026|2027))?')
COMBO = re.compile(RANGE.pattern + '|' + SINGLE.pattern)
ISO = re.compile(r'\b(2026-1[12]-\d\d|2027-0[1-3]-\d\d)\b'); DMY = re.compile(r'\b(\d\d)-(\d\d)-(2026|2027)\b')
TFS = re.compile(r'tfs=([A-Za-z0-9_-]+)')

def map_range(mm, f):
    m2 = mm.group('m2'); d2 = parse_dm(mm.group('d2'), m2, mm.group('y2'))
    m1 = mm.group('m1') or m2
    d1 = parse_dm(mm.group('d1'), m1, mm.group('y1') or (str(d2.year) if not mm.group('m1') else None))
    if not mm.group('m1') and d1 > d2: d1 = parse_dm(mm.group('d1'), MNAME[(d2.month - 2) % 12 + 1])
    n1, n2 = f(d1), f(d2)
    same = n1.month == n2.month and not mm.group('m1')
    left = (f'{WD[n1.weekday()]} ' if mm.group('wd1') else '') + (f'{n1.day}' if same else fmt(n1, wd=False)) + (f' {n1.year}' if mm.group('y1') else '')
    right = fmt(n2, wd=bool(mm.group('wd2')), year=bool(mm.group('y2')))
    return f'{left} → {right}'

def map_single(mm, f):
    d = parse_dm(mm.group('d'), mm.group('m'), mm.group('y')); n = f(d)
    return fmt(n, wd=bool(mm.group('wd')), year=bool(mm.group('y')))

def map_text(s, f, weekday_only=False):
    """Map plan dates in a piece of text. weekday_only: only 'Ddd D Mon' singles (prose)."""
    if not weekday_only:   # one combined pass, so a range's end date is not mapped a second time
        return COMBO.sub(lambda mm: map_range(mm, f) if mm.group('d1') else map_single(mm, f), s)
    return SINGLE.sub(lambda mm: map_single(mm, f) if mm.group('wd') else mm.group(0), s)

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

TAG_DROP = re.compile(r'^(?:[Dd]ay \d+|.*(?:Christmas|New Year|Carnaval|Día del Estado|Alasitas).*)$')

def in_block(blocks, d, label=None):
    for b in blocks:
        if (label is None or b[0] == label) and b[1] <= d <= b[2]: return b
    return None

def process_guide(path, old_blocks, new_blocks, f, events, convert, warn):
    t = open(path).read(); out = []; changed = 0
    for line in t.split('\n'):
        orig = line
        # 1) day-table rows: | **<date or Day N · date>** … |
        m = re.match(rf'^\| \*\*(?:(?P<lab>[^*|]+?) · )?Day (?P<n>\d+)\*\* · (?P<date>{WDR} \d{{1,2}} {MR})(?P<tags>[^|]*)\|(?P<rest>.*)$', line)
        if m and old_blocks:
            lab = m.group('lab'); n = int(m.group('n'))
            nb = next((b for b in new_blocks if b[0] == lab), None)
            if nb:
                nd = nb[1] + TD(days=n - 1); line = day_row(lab, n, nd, m.group('tags'), m.group('rest'), events)
        else:
            m = re.match(rf'^\| \*\*(?P<date>{WDR} \d{{1,2}} {MR})\*\*(?P<tags>[^|]*)\|(?P<rest>.*)$', line)
            if m and convert and old_blocks:
                d = parse_dm(*m.group('date').split()[1:]); b = in_block(old_blocks, d)
                if b:
                    n = (d - b[1]).days + 1; nb = next((x for x in new_blocks if x[0] == b[0]), b)
                    line = day_row(b[0], n, nb[1] + TD(days=n - 1), m.group('tags'), m.group('rest'), events)
                else:
                    line = map_text(line, f)
            elif m:
                line = map_text(line, f)
            elif line.startswith('|'):
                line = '|'.join(c if FIXED_KW.search(c) else map_text(c, f) for c in line.split('|'))
            elif line.startswith('> **'):
                line = ' · '.join(c if FIXED_KW.search(c) else map_text(c, f) for c in line.split(' · '))
                line = trip_days(line)
            elif line.startswith('#') or line.startswith('**Beds**'):
                line = map_text(line, f)
            else:
                # prose: relative markers first, then weekday dates outside fixed-event sentences
                line = re.sub(rf'(?:(?P<lab>[A-Z][\w ]+?) · )?Day (?P<n>\d+) \((?P<date>{WDR} \d{{1,2}} {MR})\)',
                              lambda mm: rel_marker(mm, new_blocks), line)
                if old_blocks:   # idempotent: only absolute bold day headers are converted
                    line = re.sub(rf'\*\*(?P<date>{WDR} \d{{1,2}} {MR})(?P<tail>[,:])',
                                  lambda mm: conv_bold(mm, old_blocks, new_blocks), line)
                    line = re.sub(rf'\*\*(?P<wd>{WDR}) (?P<d>\d{{1,2}})(?P<tail>[,:])',
                                  lambda mm: conv_bold_nomonth(mm, old_blocks, new_blocks), line)
                parts = re.split(r'(?<=[.;!?])\s+', line)
                line = ' '.join(p if FIXED_KW.search(p) or re.search(r'Day \d+ \(', p) else map_text(p, f, weekday_only=True) for p in parts) if parts else line
        line = map_urls(line, f)
        if line != orig: changed += 1
        out.append(line)
    new = '\n'.join(out)
    return new, changed

TRIP1 = [None]
def trip_days(line):
    rm = RANGE.search(line)
    if rm and '(days ' in line:
        d1 = parse_dm(rm.group('d1'), rm.group('m1') or rm.group('m2'), rm.group('y1') or rm.group('y2'))
        d2 = parse_dm(rm.group('d2'), rm.group('m2'), rm.group('y2'))
        if d1 > d2: d1 = d1.replace(year=d1.year - 1)
        a, b = (d1 - TRIP1[0]).days + 1, (d2 - TRIP1[0]).days + 1
        line = re.sub(r'\(days \d+–\d+\)', f'(days {a}–{b})', line, count=1)
    line = re.sub(rf'\*\*Day \d+ · (?P<d>{WDR} \d{{1,2}} {MR} (?:2026|2027))',
                  lambda mm: (lambda d: f'**Day {(d - TRIP1[0]).days + 1} · {mm.group("d")}')(parse_dm(*mm.group('d').split()[1:])), line)
    return line

def day_row(lab, n, nd, tags, rest, events):
    keep = [x.strip() for x in tags.split(' · ') if x.strip() and not TAG_DROP.match(x.strip())]
    ev = [e['label'] for e in events if e['date'] == nd.isoformat()]
    tag = ''.join(f' · {x}' for x in keep + ev)
    head = (f'{lab} · ' if lab else '') + f'Day {n}'
    return f'| **{head}** · {fmt(nd)}{tag} |{rest}'

def rel_marker(mm, new_blocks):
    lab = mm.group('lab'); n = int(mm.group('n'))
    nb = next((b for b in new_blocks if b[0] == lab), None) if lab else (new_blocks[0] if new_blocks else None)
    if not nb: return mm.group(0)
    return (f'{lab} · ' if lab else '') + f'Day {n} ({fmt(nb[1] + TD(days=n - 1))})'

def conv_bold_nomonth(mm, old_blocks, new_blocks):
    for b in old_blocks:   # find the block day with this weekday and day-of-month
        d = b[1]
        while d <= b[2]:
            if d.day == int(mm.group('d')) and WD[d.weekday()] == mm.group('wd'):
                n = (d - b[1]).days + 1; nb = next((x for x in new_blocks if x[0] == b[0]), b)
                return f'**{(b[0] + " · ") if b[0] else ""}Day {n} ({fmt(nb[1] + TD(days=n - 1))}){mm.group("tail")}'
            d += TD(days=1)
    return mm.group(0)

def conv_bold(mm, old_blocks, new_blocks):
    d = parse_dm(*mm.group('date').split()[1:]); b = in_block(old_blocks, d)
    if not b: return mm.group(0)
    n = (d - b[1]).days + 1; nb = next((x for x in new_blocks if x[0] == b[0]), b)
    lab = f'{b[0]} · ' if b[0] else ''
    return f'**{lab}Day {n} ({fmt(nb[1] + TD(days=n - 1))}){mm.group("tail")}'

def itinerary(path, f):
    t = open(path).read(); out = []; sec = ''
    for line in t.split('\n'):
        if line.startswith('## '): sec = line
        if line.startswith('|') and (sec.startswith('## At a glance') or sec.startswith('## Book these first')):
            line = map_urls(map_text(line, f), f)
        out.append(line)
    return '\n'.join(out)

WEEKDAY_SENSITIVE = re.compile(r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)(?:day)?s? only|Mon–Fri|Mon–Sat|Tue–Sun|Wed–Sun|weekdays|weekend|'
                               r'Sundays?|Saturdays?|\b(?:Wed|Sat)/(?:Wed|Sat)\b|closed (?:on )?(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)|no Sunday|no bus Sat', re.I)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--apply', action='store_true'); a = ap.parse_args()
    S = json.load(open(SCHED)); new_stays, new_blocks = compute(S)
    if os.path.exists(LOCK):
        L = json.load(open(LOCK)); old_S = dict(S, start=L['start'], stays=L['stays']); first_run = False
    else:
        old_S = S; first_run = True
    old_stays, old_blocks = compute(old_S); f = mapper(old_stays, new_stays)
    events = S.get('fixed_events', []); TRIP1[0] = D.fromisoformat(S.get('trip_day_1', S['start']))
    print(f"Trip: {new_stays[0]['arr']} → {new_stays[-1]['dep']} ({(new_stays[-1]['dep'] - new_stays[0]['arr']).days} nights)" + ('  [first run: converting to relative days, no shift]' if first_run else ''))
    old_by = {s['id']: s for s in old_stays}
    shifts = {}
    for s in new_stays:
        o = old_by.get(s['id']); delta = (s['arr'] - o['arr']).days if o else None
        flag = '' if delta == 0 else (f'  shift {delta:+d} d' if delta is not None else '  NEW')
        ev = [e['label'] for e in events if s['arr'] <= D.fromisoformat(e['date']) < max(s['dep'], s['arr'] + TD(days=1))]
        print(f"  {fmt(s['arr'])} → {fmt(s['dep'])}  {s['nights']} n  {s['id']:22} {s.get('kind','')}{flag}{'  ⚑ ' + ', '.join(sorted(set(ev))) if ev else ''}")
        shifts[s['guide']] = shifts.get(s['guide']) or (delta not in (0, None))
    opt = {o['guide']: o for o in S.get('optional', [])}
    files = sorted(glob.glob(os.path.join(GUIDES, '*.md'))); report = []
    for p in files:
        g = os.path.basename(p)[:-3]
        if g in REGION: continue
        if g in opt:  # optional guides move with their anchor
            anc = opt[g]['anchor']; delta = (next(s for s in new_stays if s['id'] == anc)['arr'] - old_by[anc]['arr'])
            ff = (lambda dlt: (lambda d: d + dlt if D(2026, 12, 1) <= d <= D(2027, 3, 31) else d))(delta)
            new, ch = process_guide(p, [], [], ff, events, False, report)
        else:
            new, ch = process_guide(p, old_blocks.get(g, []), new_blocks.get(g, []), f, events, True, report)
        old = open(p).read()
        if new != old:
            print(f'  {g}: {ch} lines change')
            if a.apply: open(p, 'w').write(new)
        if not first_run and (shifts.get(g) or g in opt):
            for i, l in enumerate(new.split('\n')):
                if WEEKDAY_SENSITIVE.search(l): report.append(f'{g}.md:{i+1}: {l.strip()[:150]}')
    ip = os.path.join(LATAM, 'itinerary.md'); new = itinerary(ip, f)
    if new != open(ip).read():
        print('  itinerary.md: dates change')
        if a.apply: open(ip, 'w').write(new)
    if report:
        print('\nRe-check these (weekday-only services, closures, events) in the guides that moved:')
        for r in report[:200]: print('  ' + r)
    if a.apply:
        json.dump({'start': S['start'], 'stays': S['stays']}, open(LOCK, 'w'), ensure_ascii=False, indent=1)
        print('\nApplied; schedule.lock.json updated.')
    else:
        print('\nDry run. Add --apply to write.')

if __name__ == '__main__':
    main()
