# Season-aware route optimizer (LatAm Dec 2026 – Mar 2027 example).
# Tries every order of the regions; scores expected wet days (monthly wet-day share from Open-Meteo 10-yr normals)
# + 2 wet-day-equivalents per 1,000 km flown; adds a travel day per long hop; keeps routes inside the window.
# D holds backpacker-consensus days only (no padding). A floating BUFFER is kept free: the plan must finish
# BUFFER days before END, so spare days can go anywhere later. The start date floats between START and START_MAX.
# Edit W (monthly wet %), D (days per region), C (coordinates), START/START_MAX/END/BUFFER. Run: python3 tools/route-optimizer/opt.py
import itertools, math, datetime as dt
# monthly expected wet-day share (Dec,Jan,Feb,Mar) from Open-Meteo 2016-2025 normals (representative places averaged)
W={'BR far NE (Jeri, Lençóis, Fortaleza)':(41,76,89,94),'BR NE coast (Pipa, Recife/Olinda)':(65,70,73,80),'BR Bahia (Salvador, Chapada Diamantina)':(50,61,58,59),
   'BR south-east (Rio, Paraty, Iguaçu)':(54,59,57,51),'Atacama + Uyuni':(16,33,37,18),'Cuba':(17,22,19,20),'Panama':(63,35,22,26),'Costa Rica':(67,57,50,52),'Nicaragua':(41,28,22,23),'Honduras (Copán, Utila)':(62,49,42,33)}
# consensus days. Brazil from blogs/Reddit/Hostelworld (21 Nov 2026); the rest provisional until research lands.
D={'BR far NE (Jeri, Lençóis, Fortaleza)':4,      # Fortaleza→Jeri 1 + Jeri 3; Lençóis lagoons are dry in Dec, so it's an optional buffer add-on
   'BR NE coast (Pipa, Recife/Olinda)':4,         # Pipa 2-3 ("11 days excessive"), Olinda 1-2
   'BR Bahia (Salvador, Chapada Diamantina)':8,   # Salvador 3, Chapada ≥4 nights (Vale do Pati 4-5 days)
   'BR south-east (Rio, Paraty, Iguaçu)':9,       # Rio 4, Paraty/Ilha Grande 2-3, Iguaçu 2
   'Atacama + Uyuni':7,                           # San Pedro 3-4 + the 3-day jeep tour to Uyuni (provisional)
   'Cuba':10,                                     # Havana 3, Viñales 2, Cienfuegos 1, Trinidad 3 (provisional)
   'Panama':7,                                    # Panama City 2, Boquete 3, Pacific islands 2 (provisional)
   'Costa Rica':10,                               # the classic 10-day loop (provisional)
   'Nicaragua':12,                                # León 3, Granada 2, Ometepe 3, San Juan del Sur 3 + 1 (provisional)
   'Honduras (Copán, Utila)':7}                   # Copán 2, Utila 4, + a transit day (provisional)
C={'SEA':(47.6,-122.3),'BR far NE (Jeri, Lençóis, Fortaleza)':(-3.7,-38.5),'BR NE coast (Pipa, Recife/Olinda)':(-7,-35),'BR Bahia (Salvador, Chapada Diamantina)':(-12.97,-39.5),
   'BR south-east (Rio, Paraty, Iguaçu)':(-23.5,-46),'Atacama + Uyuni':(-21.5,-67.5),'Cuba':(22,-80),'Panama':(9,-79.5),'Costa Rica':(10,-84.3),'Nicaragua':(12.4,-86.5),'Honduras (Copán, Utila)':(15.5,-88)}
BR=['BR far NE (Jeri, Lençóis, Fortaleza)','BR NE coast (Pipa, Recife/Olinda)','BR Bahia (Salvador, Chapada Diamantina)','BR south-east (Rio, Paraty, Iguaçu)']
def km(a,b):
    (la1,lo1),(la2,lo2)=C[a],C[b]; p=math.pi/180
    return 6371*2*math.asin(math.sqrt(math.sin((la2-la1)*p/2)**2+math.cos(la1*p)*math.cos(la2*p)*math.sin((lo2-lo1)*p/2)**2))
START=dt.date(2026,12,1); START_MAX=dt.date(2026,12,20)  # on the road for the whole Christmas/New Year stretch
END=dt.date(2027,3,15); BUFFER=14
def month_idx(d): return {12:0,1:1,2:2,3:3}.get(d.month,3)
def evaluate(seq,start):
    day=start; wet=0; legs=[]; tot=0; prev='SEA'
    for b in seq:
        k=km(prev,b); tot+=k
        if k>1500: day+=dt.timedelta(days=1)   # long hop = a travel day
        s=day
        for i in range(D[b]): wet+=W[b][month_idx(day)]/100; day+=dt.timedelta(days=1)
        legs.append((b,s,day)); prev=b
    tot+=km(prev,'SEA')
    return wet, tot, day, legs
others=['Atacama + Uyuni','Cuba','Panama','Costa Rica','Nicaragua','Honduras (Copán, Utila)']
res=[]
for off in range((START_MAX-START).days+1):
    start=START+dt.timedelta(days=off)
    for brdir in (BR, BR[::-1]):
        for perm in itertools.permutations(others):
            for pos in range(len(perm)+1):
                seq=list(perm[:pos])+brdir+list(perm[pos:])
                wet,tot,end,legs=evaluate(seq,start)
                if end+dt.timedelta(days=BUFFER)>END+dt.timedelta(days=1): continue
                score=wet+2*tot/1000   # 2 wet-day-equivalents per 1,000 km flown
                res.append((score,wet,tot,start,end,legs))
res.sort(key=lambda r:(r[0],r[3]))
print('evaluated',len(res),'feasible (route, start) pairs')
def show(r,title):
    slack=(END+dt.timedelta(days=1)-r[4]).days
    print(f"\n{title}: score {r[0]:.1f} | expected wet days {r[1]:.1f} | flown ≈{r[2]:,.0f} km | {r[3]:%d %b} → {r[4]:%d %b} ({(r[4]-r[3]).days} days) | free after: {slack} days (buffer {BUFFER})")
    for b,s_,e in r[5]: print(f"  {s_:%d %b} → {e:%d %b}  {b}")
seen=set(); k=0
for r in res:
    key=tuple(b for b,_,_ in r[5])
    if key in seen: continue
    seen.add(key); k+=1; show(r,f'#{k}')
    starts=[x[3] for x in res if tuple(b for b,_,_ in x[5])==key and x[0]<=r[0]+0.5]
    print(f"  start window within +0.5 score: {min(starts):%d %b} – {max(starts):%d %b}")
    if k==3: break
alt=[r for r in res if r[5][0][0].startswith('BR')]
if alt: show(alt[0],'Best route starting in Brazil (comparison)')
print('\nDays needed: '+', '.join(f'{k.split(" (")[0]} {v}' for k,v in D.items())+f' = {sum(D.values())} + travel days; window = {(END-START).days+1} days, {BUFFER} kept as floating buffer')
