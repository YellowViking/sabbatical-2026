# Season-aware route optimizer (LatAm Dec 2026 – Mar 2027 example).
# Tries every order of the regions; scores expected wet days (monthly wet-day share from Open-Meteo 10-yr normals)
# + 2 wet-day-equivalents per 1,000 km flown; adds a travel day per long hop; keeps routes inside the window.
# Edit W (monthly wet %), D (days per region), C (coordinates), START/END. Run: python3 tools/route-optimizer/opt.py
import itertools, math, datetime as dt
# monthly expected wet-day share (Dec,Jan,Feb,Mar) from Open-Meteo 2016-2025 normals (representative places averaged)
W={'BR far NE (Jeri, Lençóis, Fortaleza)':(41,76,89,94),'BR NE coast (Pipa, Recife/Olinda)':(65,70,73,80),'BR Bahia (Salvador, Chapada Diamantina)':(50,61,58,59),
   'BR south-east (Rio, Paraty, Iguaçu)':(54,59,57,51),'Atacama + Uyuni':(16,33,37,18),'Cuba':(17,22,19,20),'Panama':(63,35,22,26),'Costa Rica':(67,57,50,52),'Nicaragua':(41,28,22,23),'Honduras (Copán, Utila)':(62,49,42,33)}
D={'BR far NE (Jeri, Lençóis, Fortaleza)':8,'BR NE coast (Pipa, Recife/Olinda)':7,'BR Bahia (Salvador, Chapada Diamantina)':8,'BR south-east (Rio, Paraty, Iguaçu)':11,
   'Atacama + Uyuni':9,'Cuba':12,'Panama':8,'Costa Rica':10,'Nicaragua':16,'Honduras (Copán, Utila)':7}
C={'SEA':(47.6,-122.3),'BR far NE (Jeri, Lençóis, Fortaleza)':(-3.7,-38.5),'BR NE coast (Pipa, Recife/Olinda)':(-7,-35),'BR Bahia (Salvador, Chapada Diamantina)':(-12.97,-39.5),
   'BR south-east (Rio, Paraty, Iguaçu)':(-23.5,-46),'Atacama + Uyuni':(-21.5,-67.5),'Cuba':(22,-80),'Panama':(9,-79.5),'Costa Rica':(10,-84.3),'Nicaragua':(12.4,-86.5),'Honduras (Copán, Utila)':(15.5,-88)}
BR=['BR far NE (Jeri, Lençóis, Fortaleza)','BR NE coast (Pipa, Recife/Olinda)','BR Bahia (Salvador, Chapada Diamantina)','BR south-east (Rio, Paraty, Iguaçu)']
def km(a,b):
    (la1,lo1),(la2,lo2)=C[a],C[b]; p=math.pi/180
    return 6371*2*math.asin(math.sqrt(math.sin((la2-la1)*p/2)**2+math.cos(la1*p)*math.cos(la2*p)*math.sin((lo2-lo1)*p/2)**2))
START=dt.date(2026,12,1); END=dt.date(2027,3,15)
def month_idx(d): return {12:0,1:1,2:2,3:3}.get(d.month,3)
def evaluate(seq):
    day=START; wet=0; legs=[]; tot=0; prev='SEA'
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
for brdir in (BR, BR[::-1]):
    for perm in itertools.permutations(others):
        for pos in range(len(perm)+1):
            seq=list(perm[:pos])+brdir+list(perm[pos:])
            wet,tot,end,legs=evaluate(seq)
            if end>END+dt.timedelta(days=1): continue
            score=wet+2*tot/1000   # 2 wet-day-equivalents per 1,000 km flown
            res.append((score,wet,tot,end,legs))
res.sort(key=lambda r:r[0])
print('evaluated',len(res),'feasible routes')
for r in res[:4]:
    print(f"\nscore {r[0]:.1f} | expected wet days {r[1]:.1f} | flown ≈{r[2]:,.0f} km | ends {r[3]}")
    for b,s,e in r[4]: print(f"  {s:%d %b} → {e:%d %b}  {b}")
# also show the best route that starts in Central America, for comparison
alt=[r for r in res if r[4][0][0].startswith('BR')]
if alt:
    r=alt[0]; print(f"\nBest route starting in Brazil (comparison): score {r[0]:.1f} | wet {r[1]:.1f} | ≈{r[2]:,.0f} km")
    for b,s,e in r[4]: print(f"  {s:%d %b} → {e:%d %b}  {b}")
print('\nDays needed: '+', '.join(f'{k.split(" (")[0]} {v}' for k,v in D.items())+f' = {sum(D.values())} + travel days; window = {(END-START).days+1} days')
