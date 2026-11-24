# Route brainstorm v5 (LatAm Dec 2026 – Mar 2027): Brazil cut to the Rio–São Paulo corridor, then the south loop,
# the Andes and Central America. Like brainstorm.py it CHOOSES optional regions and permutes geographic chains,
# and it also scores crowd/price peaks (Brazil's school holidays + Carnival, Uruguay's January, Central America's
# Christmas–New Year) so the comparison isn't weather-only.
# Score = value of days (1.0 new country, VISITED for a visited one) − expected wet days (highland ×HR)
#         − PEAK per day spent in a region's peak − 2 per 1,000 km moved. Must end BUFFER days before END.
# Run: python3 tools/route-optimizer/brainstorm_v5.py     (env: HR, VISITED, PEAK, BUFFER)
import itertools, math, os, datetime as dt
D_ = dt.date
# name: (wet-day % Dec,Jan,Feb,Mar — Open-Meteo 2016-25, day ≥1 mm, averaged over the named places), typical days, (lat,lon), highland, new country, peak periods
R = {
 'Bahia (Salvador, Boipeba/Morerê, Chapada)': ((50,61,58,59),10, (-12.97,-39.5), False, True,  [(D_(2026,12,20), D_(2027,2,10))]),  # a friend's tip, 24 Nov: Morerê (Boipeba) + Chapada
 'Rio–São Paulo (Rio, Ilha Grande, Paraty, SP)': ((61,67,64,57), 9, (-23.0,-44.5), False, True,  [(D_(2026,12,20), D_(2027,2,10))]),
 'Iguaçu (+ Curitiba)':                      ((45,53,46,42), 3, (-25.55,-54.58),False, True,  [(D_(2026,12,20), D_(2027,2,10))]),
 'Paraguay (Asunción, Encarnación)':         ((37,41,38,37), 4, (-26.3,-56.7),  False, True,  []),
 'Buenos Aires':                             ((26,27,25,29), 3, (-34.6,-58.4),  False, False, []),
 'Uruguay (Colonia, Montevideo, Cabo Polonio)': ((28,30,35,35), 6, (-34.6,-55.5), False, True, [(D_(2026,12,24), D_(2027,2,15))]),
 'Central Chile (Santiago, Valparaíso)':     ((3,2,2,3),     5, (-33.2,-71.1),  False, True,  []),
 'Córdoba + Sierras (Mendoza = transit)':    ((36,45,42,40), 5, (-31.4,-64.4),  False, False, []),   # replaces Mendoza (visited); Feb/Mar wet % estimated
 'NW Argentina (Salta, Jujuy, Cafayate)':    ((61,67,63,54), 7, (-24.5,-65.5),  True,  False, []),
 'Atacama + Uyuni':                          ((16,33,37,18), 8, (-21.5,-67.5),  True,  True,  []),
 'Bolivia cities (Sucre, Potosí, La Paz)':   ((69,75,78,70), 7, (-18,-66.5),    True,  True,  []),
 'Titicaca (Copacabana, Puno)':              ((80,86,93,86), 3, (-16,-69.5),    True,  True,  []),
 'S Peru highlands (Arequipa, Colca)':       ((38,67,80,73), 4, (-16,-71.6),    True,  False, []),
 'Peru coast (Huacachina, Paracas, Lima)':   ((3,13,17,8),   5, (-13.9,-76),    False, False, []),
 'Panama':                                   ((63,35,22,26), 6, (9,-79.5),      False, True,  [(D_(2026,12,20), D_(2027,1,5))]),
 'Costa Rica':                               ((67,57,50,52),10, (10,-84.3),     False, True,  [(D_(2026,12,20), D_(2027,1,5))]),
 'Nicaragua':                                ((41,28,22,23),14, (12.4,-86.5),   False, True,  [(D_(2026,12,20), D_(2027,1,5))]),
 'Honduras (Copán, Utila)':                  ((62,49,42,33), 8, (15.5,-88),     False, True,  []),
}
MUST = {'Rio–São Paulo (Rio, Ilha Grande, Paraty, SP)','Iguaçu (+ Curitiba)','Paraguay (Asunción, Encarnación)',
        'Uruguay (Colonia, Montevideo, Cabo Polonio)','Central Chile (Santiago, Valparaíso)','Atacama + Uyuni',
        'Bolivia cities (Sucre, Potosí, La Paz)','Costa Rica','Nicaragua'}
for r in filter(None, os.environ.get('MUSTADD','').split(',')): MUST.add(next(k for k in R if k.startswith(r)))
for r in filter(None, os.environ.get('DROP','').split(',')): R.pop(next(k for k in R if k.startswith(r)))
for kv in filter(None, os.environ.get('DAYS','').split(',')):
    k, v = kv.split('='); k = next(x for x in R if x.startswith(k)); R[k] = R[k][:1] + (int(v),) + R[k][2:]
CHAINS = {  # each chain runs in this order or reversed, skipping unselected regions; chains are permuted
 'EAST':  ['Bahia (Salvador, Boipeba/Morerê, Chapada)','Rio–São Paulo (Rio, Ilha Grande, Paraty, SP)','Iguaçu (+ Curitiba)','Paraguay (Asunción, Encarnación)','Buenos Aires',
           'Uruguay (Colonia, Montevideo, Cabo Polonio)'],
 'CHILE': ['Córdoba + Sierras (Mendoza = transit)','Central Chile (Santiago, Valparaíso)'],
 'ANDES': ['NW Argentina (Salta, Jujuy, Cafayate)','Atacama + Uyuni','Bolivia cities (Sucre, Potosí, La Paz)','Titicaca (Copacabana, Puno)',
           'S Peru highlands (Arequipa, Colca)','Peru coast (Huacachina, Paracas, Lima)'],
 'CA':    ['Panama','Costa Rica','Nicaragua','Honduras (Copán, Utila)'],
}
CHAINS = {c: [r for r in v if r in R] for c, v in CHAINS.items()}
START = D_(2026,12,1); START_MAX = D_(2026,12,20); END = D_(2027,3,15); BUFFER = int(os.environ.get('BUFFER', 14)); STEP = 2
HR = float(os.environ.get('HR', 0.5)); PEAK = float(os.environ.get('PEAK', 0.5)); KM_COST = 2/1000
VALUE = {True: 1.0, False: float(os.environ.get('VISITED', 0.8))}
HOME = (47.6,-122.3)
def km(a, b):
    (la1,lo1),(la2,lo2) = a,b; p = math.pi/180
    return 6371*2*math.asin(math.sqrt(math.sin((la2-la1)*p/2)**2+math.cos(la1*p)*math.cos(la2*p)*math.sin((lo2-lo1)*p/2)**2))
NDAYS = (END-START).days + 40; mon = {12:0,1:1,2:2,3:3}
wetp, peakp = {}, {}
for r,(w,_,_,hi,_,pk) in R.items():
    a, b = [0.0], [0.0]
    for i in range(NDAYS):
        d = START + dt.timedelta(days=i)
        a.append(a[-1] + w[mon.get(d.month,3)]/100*(HR if hi else 1)); b.append(b[-1] + any(s <= d < e for s,e in pk))
    wetp[r], peakp[r] = a, b
def evaluate(seq, off):
    day = off; wet = peak = tot = 0; prev = HOME; legs = []
    for r in seq:
        k = km(prev, R[r][2]); tot += k
        if k > 1500: day += 1
        n = R[r][1]; wet += wetp[r][day+n]-wetp[r][day]; peak += peakp[r][day+n]-peakp[r][day]
        legs.append((r, day, day+n)); day += n; prev = R[r][2]
    return wet, peak, tot + km(prev, HOME), day, legs
optional = [r for r in R if r not in MUST]
limit = (END-START).days + 1 - BUFFER
SCEN = {'best overall': lambda s: True,
        'South America first': lambda s: s[-1] in CHAINS['CA'], 'Central America first': lambda s: s[0] in CHAINS['CA'],
        'enter Rio': lambda s: s[0].startswith('Rio'), 'enter Santiago': lambda s: s[0].startswith('Central Chile'),
        'enter Santiago, then fly to Rio': lambda s: s[0].startswith('Central Chile') and any(x.startswith('Rio') for x in s[1:3]),
        'enter Santiago, Andes north first': lambda s: s[0].startswith('Central Chile') and s.index('Atacama + Uyuni') < s.index('Iguaçu (+ Curitiba)')}
best = {k: None for k in SCEN}
for mask in range(1 << len(optional)):
    sel = MUST | {optional[i] for i in range(len(optional)) if mask >> i & 1}
    if sum(R[r][1] for r in sel) > limit: continue
    value = sum(R[r][1]*VALUE[R[r][4]] for r in sel)
    units = [c for c in CHAINS if any(r in sel for r in CHAINS[c])]
    for perm in itertools.permutations(units):
        for ds in itertools.product([0,1], repeat=len(perm)):
            seq = []
            for c, d in zip(perm, ds):
                ch = [r for r in CHAINS[c] if r in sel]; seq += ch if d == 0 else ch[::-1]
            tags = [k for k,f in SCEN.items() if f(seq)]
            for off in range(0, (START_MAX-START).days+1, STEP):
                wet, peak, tot, end, legs = evaluate(seq, off)
                if end > limit: continue
                score = value - wet - PEAK*peak - KM_COST*tot
                for k in tags:
                    if best[k] is None or score > best[k][0]: best[k] = (score, wet, peak, tot, off, end, legs, sel)
fmt = lambda o: (START+dt.timedelta(days=o)).strftime('%d %b')
print(f"limit {limit} days of typical stays (window {START:%d %b}–{END:%d %b}, {BUFFER}-day floating buffer); HR={HR} PEAK={PEAK} VISITED={VALUE[False]}")
for k, b in best.items():
    if not b: print(f"\n{k}: no feasible plan"); continue
    score, wet, peak, tot, off, end, legs, sel = b
    print(f"\n{k}: score {score:.1f} | {sum(R[r][1] for r in sel)} days | wet {wet:.1f} | peak days {peak:.0f} | ≈{tot:,.0f} km | {fmt(off)} → {fmt(end)} | dropped: "
          + (', '.join(r.split(' (')[0] for r in optional if r not in sel) or '—'))
    for r, s, e in legs: print(f"   {fmt(s)} → {fmt(e)}  {r}")
