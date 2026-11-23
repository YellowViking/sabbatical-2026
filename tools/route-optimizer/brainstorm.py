# Region-selection route brainstorm (LatAm Dec 2026 – Mar 2027).
# Unlike opt.py (fixed region list), this also CHOOSES which optional regions to include.
# Regions sit in geographic chains (kept in order, either direction); chains and singles are permuted.
# Score = value of days spent in new places − expected wet days (highland rain at half weight: storms pass, mornings clear)
#         − 2 per 1,000 km moved. Plan must end BUFFER days before END; start floats START..START_MAX.
# Run: python3 tools/route-optimizer/brainstorm.py
import itertools, math, os, datetime as dt

# name: (wet-day % Dec,Jan,Feb,Mar from Open-Meteo 2016-25 normals, typical days, (lat,lon), highland?, new country?)
R = {
 'BR far NE (Jeri, Fortaleza)':            ((41,76,89,94), 4, (-3.7,-38.5),  False, True),
 'BR NE coast (Canoa, Pipa, Olinda)':      ((65,70,73,80), 5, (-7,-35),      False, True),
 'BR Bahia (Salvador, Chapada)':           ((50,61,58,59), 8, (-12.97,-39.5),False, True),
 'BR south-east (Rio, Ilha Grande, Paraty, Iguaçu)': ((54,59,57,51), 9, (-23.5,-46), False, True),
 'Uruguay (Montevideo, Cabo Polonio)':     ((28,30,35,35), 6, (-34.6,-55.5), False, True),
 'Central Chile (Santiago, Valparaíso)':   ((3,2,2,3),     5, (-33.2,-71.1), False, True),
 'NW Argentina (Salta, Jujuy, Cafayate)':  ((61,67,63,54), int(os.environ.get('NWA',7)), (-24.5,-65.5), True,  False),
 'Atacama + Uyuni':                        ((16,33,37,18), 8, (-21.5,-67.5), True,  True),
 'Bolivia cities (Sucre, Potosí, La Paz)': ((69,75,78,70), 7, (-18,-66.5),   True,  True),
 'Titicaca (Copacabana, Puno)':            ((80,86,93,86), 3, (-16,-69.5),   True,  True),
 'S Peru highlands (Arequipa, Colca)':     ((38,67,80,73), 4, (-16,-71.6),   True,  False),
 'Peru coast (Nazca, Huacachina, Paracas, Lima)': ((3,13,17,8), 5, (-13.9,-76), False, False),
 'Panama':                                 ((63,35,22,26), 6, (9,-79.5),     False, True),
 'Costa Rica':                             ((67,57,50,52),10, (10,-84.3),    False, True),
 'Nicaragua':                              ((41,28,22,23),14, (12.4,-86.5),  False, True),
 'Honduras (Copán, Utila)':                ((62,49,42,33), 8, (15.5,-88),    False, True),
 'S Mexico (Chiapas, Palenque, Mérida, Bacalar)': ((32,30,23,21),11, (18.5,-90.5), False, False),
 'Dominican Republic':                     ((50,42,52,49), 7, (18.9,-70.2),  False, True),
}
MUST = {'BR far NE (Jeri, Fortaleza)','BR NE coast (Canoa, Pipa, Olinda)','BR Bahia (Salvador, Chapada)',
        'BR south-east (Rio, Ilha Grande, Paraty, Iguaçu)','Atacama + Uyuni','Costa Rica','Nicaragua'}
CHAINS = {  # geographic order; a chain is used in this order or reversed, skipping regions not selected
 'BR':    ['BR far NE (Jeri, Fortaleza)','BR NE coast (Canoa, Pipa, Olinda)','BR Bahia (Salvador, Chapada)',
           'BR south-east (Rio, Ilha Grande, Paraty, Iguaçu)','Uruguay (Montevideo, Cabo Polonio)'],
 'ANDES': ['Central Chile (Santiago, Valparaíso)','NW Argentina (Salta, Jujuy, Cafayate)','Atacama + Uyuni',
           'Bolivia cities (Sucre, Potosí, La Paz)','Titicaca (Copacabana, Puno)','S Peru highlands (Arequipa, Colca)',
           'Peru coast (Nazca, Huacachina, Paracas, Lima)'],
 'CA':    ['Panama','Costa Rica','Nicaragua','Honduras (Copán, Utila)','S Mexico (Chiapas, Palenque, Mérida, Bacalar)'],
 'DR':    ['Dominican Republic'],
}
FIXED_DIR = {'BR': [0]}   # Brazil runs north → south (dry NE in early Dec, holiday prices later); set [0,1] to test both
START = dt.date(2026,12,1); START_MAX = dt.date(2026,12,20); END = dt.date(2027,3,15); BUFFER = 14
STEP = 2                  # test every 2nd start day
HIGHLAND_RAIN = float(os.environ.get('HR', 0.5))      # highland storms mostly pass; mornings usable
KM_COST = 2/1000
VALUE = {True: 1.0, False: float(os.environ.get('VISITED', 0.8))}   # per day: new country vs new region in a visited country

HOME = (47.6,-122.3)
def km(a, b):
    (la1,lo1),(la2,lo2) = a,b; p = math.pi/180
    return 6371*2*math.asin(math.sqrt(math.sin((la2-la1)*p/2)**2+math.cos(la1*p)*math.cos(la2*p)*math.sin((lo2-lo1)*p/2)**2))

# daily rain cost per region, as prefix sums over the calendar
D0 = START; NDAYS = (END - START).days + 40
mon = {12:0,1:1,2:2,3:3}
pref = {}
for r,(w,_,_,hi,_) in R.items():
    acc=[0.0]
    for i in range(NDAYS):
        d = D0 + dt.timedelta(days=i); m = mon.get(d.month, 3)
        acc.append(acc[-1] + w[m]/100*(HIGHLAND_RAIN if hi else 1))
    pref[r]=acc

def evaluate(seq, off):
    day = off; wet = 0; tot = 0; prev = HOME; legs = []
    for r in seq:
        k = km(prev, R[r][2]); tot += k
        if k > 1500: day += 1
        n = R[r][1]; wet += pref[r][day+n] - pref[r][day]
        legs.append((r, day, day+n)); day += n; prev = R[r][2]
    tot += km(prev, HOME)
    return wet, tot, day, legs

optional = [r for r in R if r not in MUST]
limit = (END - START).days + 1 - BUFFER
best_by_set = {}
for mask in range(1 << len(optional)):
    sel = MUST | {optional[i] for i in range(len(optional)) if mask >> i & 1}
    if sum(R[r][1] for r in sel) > limit: continue
    units = [c for c in CHAINS if any(r in sel for r in CHAINS[c])]
    best = None
    for perm in itertools.permutations(units):
        dirs = [FIXED_DIR.get(c, [0,1]) for c in perm]
        for ds in itertools.product(*dirs):
            seq = []
            for c, d in zip(perm, ds):
                ch = [r for r in CHAINS[c] if r in sel]
                seq += ch if d == 0 else ch[::-1]
            for off in range(0, (START_MAX-START).days+1, STEP):
                wet, tot, end, legs = evaluate(seq, off)
                if end > limit: continue
                value = sum(R[r][1]*VALUE[R[r][4]] for r in sel)
                score = value - wet - KM_COST*tot
                if best is None or score > best[0]: best = (score, wet, tot, off, end, legs, value)
    if best: best_by_set[frozenset(sel)] = best

ranked = sorted(best_by_set.items(), key=lambda kv: -kv[1][0])
fmt = lambda off: (START + dt.timedelta(days=off)).strftime('%d %b')
def show(sel, b, title):
    score, wet, tot, off, end, legs, value = b
    days = sum(R[r][1] for r in sel)
    print(f"\n{title}: score {score:.1f} | {days} days in {len(sel)} regions | wet {wet:.1f} (highland ×{HIGHLAND_RAIN}) | ≈{tot:,.0f} km | "
          f"{fmt(off)} → {fmt(end)} | free after: {limit + BUFFER - end} days (incl. {BUFFER} buffer)")
    for r, s, e in legs: print(f"   {fmt(s)} → {fmt(e)}  {r}")
print(f"evaluated {len(best_by_set)} feasible region sets")
for i, (sel, b) in enumerate(ranked[:3]): show(sel, b, f"#{i+1}")
# best route per number of optional regions, to see the trade-off curve
seen = set()
for sel, b in ranked:
    n = len(sel) - len(MUST)
    if n in seen: continue
    seen.add(n); days = sum(R[r][1] for r in sel)
    print(f"  best with {n} optional: score {b[0]:.1f}, {days} days, wet {b[1]:.1f}, ≈{b[2]:,.0f} km: "
          + ', '.join(r.split(' (')[0] for r in sel if r not in MUST))
