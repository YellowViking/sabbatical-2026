# LatAm draft route map (Dec 2026 – Mar 2027), same style as make_map.py. Usage:
#   curl -sLo /tmp/countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
#   python3 tools/route-map/latam_plan_map.py /tmp/countries.geojson trips/latam/latam-route-draft.svg
# Edit S (stops), L (legs by mode) and the Central America inset to redraw the plan.
import json, math, sys
GEO = sys.argv[1]; OUT = sys.argv[2]
LON0, LON1, LAT0, LAT1 = -95.0, -24.0, -36.5, 19.5
W = 1000; K = math.cos(math.radians(-8)); SX = W / ((LON1 - LON0) * K); H_MAP = (LAT1 - LAT0) * SX
TOP = 96; PAD_B = 400; H = int(TOP + H_MAP + PAD_B)
def P(lat, lon): return ((lon - LON0) * K * SX, TOP + (LAT1 - lat) * SX)

# --- stops: (n, name, dates, lat, lon, label dx, dy, anchor); CA=True → drawn in the inset
S = [
 (1,'Rio de Janeiro','4–8 Dec',-22.7,-42.9, 12,-6,'start'),
 (2,'Ilha Grande','8–10 Dec',-23.8,-44.0, 12,12,'start'),
 (3,'Paraty','10–11 Dec',-23.1,-45.45, -2,26,'end'),
 (4,'São Paulo','11–13 Dec',-23.7,-47.0, -12,4,'end'),
 (5,'Jericoacoara','13–16 Dec',-2.79,-40.51, -12,-6,'end'),
 (6,'Canoa Quebrada','16–18 Dec',-4.53,-37.69, 12,-6,'start'),
 (7,'Pipa','18–21 Dec',-6.23,-35.05, 12,4,'start'),
 (8,'Olinda + Recife','21–23 Dec',-8.01,-34.86, 12,6,'start'),
 (9,'Maceió','23–24 Dec',-9.67,-35.74, 12,6,'start'),
 (10,'Salvador','24–27 Dec · 31 Dec–2 Jan',-12.97,-38.5, 12,4,'start'),
 (11,'Chapada Diamantina','27–31 Dec',-12.56,-41.39, -12,-6,'end'),
 (12,'Punta del Diablo + Cabo Polonio','≈ early Jan',-34.1,-53.6, 12,4,'start'),
 (13,'Montevideo','≈ early Jan',-34.9,-56.16, 10,16,'start'),
 (14,'Colonia','≈ early Jan',-34.47,-57.84, -12,14,'end'),
 (15,'Encarnación','≈ mid-Jan',-27.33,-55.87, 12,8,'start'),
 (16,'Asunción','≈ mid-Jan',-25.28,-57.63, -4,-12,'end'),
 (17,'Iguaçu Falls','≈ mid-Jan',-25.6,-54.5, 12,18,'start'),
 (18,'Santiago','≈ mid-Jan',-33.45,-70.67, 10,18,'start'),
 (19,'Valparaíso','≈ mid-Jan',-33.05,-71.62, -12,4,'end'),
 (20,'Mendoza','≈ late Jan',-32.89,-68.84, 12,-4,'start'),
 (21,'Cafayate','≈ late Jan',-26.07,-65.98, -12,8,'end'),
 (22,'Salta','≈ late Jan',-24.79,-65.41, -12,6,'end'),
 (23,'Purmamarca / Tilcara','≈ late Jan',-23.6,-65.4, 12,-6,'start'),
 (24,'San Pedro de Atacama','≈ late Jan',-22.91,-68.2, -12,4,'end'),
 (25,'Uyuni','jeep tour · ≈ early Feb',-20.8,-67.15, -12,12,'end'),
 (26,'Potosí','≈ early Feb',-19.95,-66.0, 12,10,'start'),
 (27,'Sucre','≈ early Feb',-18.75,-64.8, 12,-2,'start'),
 (28,'La Paz','≈ early Feb',-16.5,-68.15, 12,4,'start'),
 (29,'Copacabana + Isla del Sol','≈ mid-Feb',-16.0,-69.1, 8,-13,'start'),
 (30,'Puno','',-15.6,-70.1, -8,-10,'end'),
 (31,'Arequipa + Colca','≈ mid-Feb',-16.5,-71.6, -12,10,'end'),
 (32,'Huacachina','≈ mid-Feb',-14.4,-75.45, -12,14,'end'),
 (33,'Paracas','≈ mid-Feb',-13.55,-76.55, -12,2,'end'),
 (34,'Lima','≈ late Feb',-11.95,-77.1, -12,-4,'end'),
 (35,'San José','≈ late Feb',9.93,-84.08, 0,0,'start'),
 (36,'La Fortuna / Arenal','≈ late Feb',10.47,-84.64, 0,0,'start'),
 (37,'Monteverde','≈ late Feb',10.3,-84.82, 0,0,'start'),
 (38,'Rincón de la Vieja','≈ early Mar',10.77,-85.35, 0,0,'start'),
 (39,'Playa Maderas / SJDS','≈ early Mar',11.3,-85.87, 0,0,'start'),
 (40,'Ometepe','≈ early Mar',11.5,-85.6, 0,0,'start'),
 (41,'Granada + Apoyo + Masaya','≈ Mar',11.93,-85.96, 0,0,'start'),
 (42,'León','≈ Mar',12.43,-86.88, 0,0,'start'),
 (43,'Copán Ruinas','optional',14.84,-89.14, 0,0,'start'),
 (44,'Utila (via La Ceiba)','optional',16.1,-86.93, 0,0,'start'),
]
OPTIONAL = {43, 44}
CA = {s[1] for s in S if s[0] >= 35}
st = {s[1]: s for s in S}
FOR, NAT, GOI, POA, CHUY, BA, POS, CDE = (-3.73,-38.52), (-5.79,-35.21), (-6.27,-35.21), (-30.03,-51.23), (-33.69,-53.46), (-34.6,-58.38), (-27.37,-55.9), (-25.51,-54.61)
TUC, JAMA, NAZ, SJO = (-26.82,-65.22), (-23.24,-67.03), (-14.83,-74.94), (9.93,-84.08)
LAG = (-22.2,-67.8); SALAR = (-20.2,-67.6)
L = [
 ('boat',['Rio de Janeiro','Ilha Grande','Paraty']),
 ('bus',['Paraty','São Paulo']),
 ('flight',['São Paulo','Jericoacoara']),
 ('bus',['Jericoacoara',FOR,'Canoa Quebrada',NAT,'Pipa',GOI,'Olinda + Recife','Maceió','Salvador']),
 ('bus',['Salvador','Chapada Diamantina']),
 ('flight',['Salvador',POA]),
 ('bus',[POA,CHUY,'Punta del Diablo + Cabo Polonio','Montevideo','Colonia']),
 ('boat',['Colonia',BA]),
 ('bus',[BA,POS,'Encarnación','Asunción',CDE,'Iguaçu Falls']),
 ('flight',['Iguaçu Falls','Santiago']),
 ('bus',['Santiago','Valparaíso']),
 ('bus',['Santiago','Mendoza',TUC,'Cafayate','Salta','Purmamarca / Tilcara',JAMA,'San Pedro de Atacama']),
 ('jeep',['San Pedro de Atacama',LAG,SALAR,'Uyuni']),
 ('bus',['Uyuni','Potosí','Sucre','La Paz','Copacabana + Isla del Sol','Puno','Arequipa + Colca',NAZ,'Huacachina','Paracas','Lima']),
 ('flight',['Lima',SJO]),
]
FORT_LAKE = (10.5,-84.85); LIB = (10.63,-85.44); SJORGE = (11.43,-85.84); LCEIBA = (15.76,-86.79); SAP = (15.5,-88.03)
CAL = [
 ('bus',['San José','La Fortuna / Arenal']),
 ('boat',['La Fortuna / Arenal',FORT_LAKE]),
 ('bus',[FORT_LAKE,'Monteverde',LIB,'Rincón de la Vieja','Playa Maderas / SJDS',SJORGE]),
 ('boat',[SJORGE,'Ometepe']),
 ('bus',['Ometepe','Granada + Apoyo + Masaya','León']),
]
CAL_OPT = [('bus',['León','Copán Ruinas',SAP,LCEIBA]), ('boat',[LCEIBA,'Utila (via La Ceiba)'])]
MODES = {  # light, dark, dash, width, label  (slots 1–4 of the validated categorical palette, fixed order)
 'flight':('#2a78d6','#3987e5','2 6',2.5,'Flight'),
 'bus':   ('#eb6834','#d95926','9 5',3,'Bus / shuttle'),
 'boat':  ('#1baf7a','#199e70','1 4',3.2,'Boat / ferry'),
 'jeep':  ('#eda100','#c98500','10 4 2 4',3,'Jeep tour (3 days)'),
}
def coords(i): return st[i][3:5] if isinstance(i,str) else i
def path(mode, items, proj):
    ps=[proj(*coords(i)) for i in items]
    if mode=='flight':
        (x1,y1),(x2,y2)=ps; mx,my=(x1+x2)/2,(y1+y2)/2; dx,dy=x2-x1,y2-y1; nx,ny=-dy,dx; n=math.hypot(nx,ny) or 1
        bend=0.16*math.hypot(dx,dy); sgn=-1 if ny>0 else 1; cx,cy=mx+nx/n*bend*sgn,my+ny/n*bend*sgn
        return f'M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}'
    return 'M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in ps)

g=json.load(open(GEO))
def ring_path(r, proj):
    out=[]; last=None
    for lon,lat in r:
        x,y=proj(lat,lon); q=(round(x,1),round(y,1))
        if last and abs(q[0]-last[0])<0.8 and abs(q[1]-last[1])<0.8: continue
        out.append(q); last=q
    return ('M'+' L'.join(f'{x},{y}' for x,y in out)+'Z') if len(out)>2 else ''
def land_paths(proj, b):
    res=[]
    for f in g['features']:
        geom=f['geometry']; polys=geom['coordinates'] if geom['type']=='MultiPolygon' else [geom['coordinates']]
        d=''
        for poly in polys:
            lons=[c[0] for c in poly[0]]; lats=[c[1] for c in poly[0]]
            if max(lons)<b[0]-2 or min(lons)>b[1]+2 or max(lats)<b[2]-2 or min(lats)>b[3]+2: continue
            for r in poly: d+=ring_path(r, proj)
        if d: res.append((f['properties'].get('NAME'), d))
    return res
CSS = """
  :root { color-scheme: light dark; }
  .surface { fill: #e6edf2; } .page { fill: #fcfcfb; } .land { fill: #fcfcfb; stroke: #d6d4cc; stroke-width: 0.8; }
  .ink { fill: #0b0b0b; } .ink2 { fill: #52514e; } .ink3 { fill: #8a8984; } .halo { stroke: #fcfcfb; } .frame { stroke: #52514e; }
  .ring { stroke: #fcfcfb; } .dot { fill: #0b0b0b; } .num { fill: #fcfcfb; } .box { fill: #fcfcfb; stroke: #52514e; }
""" + ''.join(f"  .m-{k} {{ stroke: {v[0]}; }} .mf-{k} {{ fill: {v[0]}; }}\n" for k,v in MODES.items()) + """
  @media (prefers-color-scheme: dark) {
    .surface { fill: #0f1418; } .page { fill: #1a1a19; } .land { fill: #1a1a19; stroke: #383835; }
    .ink { fill: #f0efec; } .ink2 { fill: #c3c2b7; } .ink3 { fill: #8f8e86; } .halo { stroke: #1a1a19; } .frame { stroke: #c3c2b7; }
    .ring { stroke: #1a1a19; } .dot { fill: #f0efec; } .num { fill: #1a1a19; } .box { fill: #1a1a19; stroke: #c3c2b7; }
""" + ''.join(f"    .m-{k} {{ stroke: {v[1]}; }} .mf-{k} {{ fill: {v[1]}; }}\n" for k,v in MODES.items()) + """  }
  .t-title { font-size: 22px; font-weight: 700; } .t-sub { font-size: 13px; }
  .t-stop { font-size: 12.5px; font-weight: 650; } .t-date { font-size: 10.5px; font-weight: 400; }
  .t-num { font-size: 9.5px; font-weight: 700; } .t-leg { font-size: 12.5px; } .t-note { font-size: 11.5px; }
  .t-country { font-size: 13px; font-weight: 600; letter-spacing: 2px; } .t-list { font-size: 11.5px; }
  .halo { stroke-width: 3.5px; stroke-linejoin: round; paint-order: stroke; }
"""
def draw_legs(o, proj, legs, op=1.0):
    for mode,items in legs:
        c=MODES[mode]; dash=f' stroke-dasharray="{c[2]}"' if c[2] else ''; d=path(mode,items,proj)
        o.append(f'<path class="ring" d="{d}" fill="none" stroke-width="{c[3]+3}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
        o.append(f'<path class="m-{mode}" d="{d}" fill="none" stroke-width="{c[3]}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"{dash}><title>{c[4]}</title></path>')
def draw_stop(o, proj, s, label=True, dates=True, r=8.5):
    n,name,dt,la,lo,dx,dy,anc=s; x,y=proj(la,lo)
    o.append(f'<g><title>{n}. {name}: {dt}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="dot ring" stroke-width="2"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" class="num t-num" text-anchor="middle">{n}</text>'
             + (f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="ink t-stop halo" text-anchor="{anc}">{name}'
                + (f' <tspan class="ink2 t-date">{dt}</tspan>' if dates else '') + '</text>' if label else '') + '</g>')

o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, -apple-system, \'Segoe UI\', sans-serif">',
   '<title>Latin America draft route (Plan B): Rio → Uruguay → Paraguay → the Andes → Central America, Dec 2026 – Mar 2027</title>', f'<style>{CSS}</style>',
   f'<rect width="{W}" height="{H}" class="page"/>', f'<rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}" class="surface"/>',
   f'<clipPath id="map"><rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}"/></clipPath>','<g clip-path="url(#map)">']
for name,d in land_paths(P,(LON0,LON1,LAT0,LAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
for name,la,lo in [('BRAZIL',-10,-52),('BOLIVIA',-17.5,-63.5),('PERU',-9,-75),('CHILE',-29,-71.6),('ARGENTINA',-30,-63),('PARAGUAY',-22.3,-58.5),('URUGUAY',-32.6,-55.9)]:
    x,y=P(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-country" text-anchor="middle">{name}</text>')
o.append('</g>')
draw_legs(o, P, L)
# Central America on the main map: dots only, framed, pointing to the inset
for s_ in S:
    if s_[1] in CA:
        x,y=P(*s_[3:5]); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>{s_[0]}. {s_[1]}: {s_[2]}</title></circle>')
    else:
        draw_stop(o, P, s_, dates=s_[0] <= 11)
# small waypoint dot: Nazca (no night)
x,y=P(*NAZ); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>Nazca: daytime stop at the viewing tower</title></circle>')
x,y=P(*st['Chapada Diamantina'][3:5]); o.append(f'<text x="{x-12:.0f}" y="{y+10:.0f}" class="ink2 t-date halo" text-anchor="end">bus there and back</text>')
# Seattle arrows
x,y=P(*st['Rio de Janeiro'][3:5]); o.append(f'<path class="m-flight" d="M{x-170:.0f},{y-250:.0f} Q{x-110:.0f},{y-90:.0f} {x-6:.0f},{y-6:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{x-170:.0f}" y="{y-256:.0f}" class="ink2 t-date halo" text-anchor="middle">✈ from Seattle, 3 Dec (Alaska award)</text>')
for nm,(la,lo),dx,dy,anc in [('Porto Alegre (change buses)',POA,10,4,'start'),('Buenos Aires (ferry, then night bus)',BA,-10,32,'end')]:
    x,y=P(la,lo); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>{nm}</title></circle><text x="{x+dx:.0f}" y="{y+dy:.0f}" class="ink2 t-date halo" text-anchor="{anc}">{nm}</text>')
bx0,by0=P(17.2,-90.2); bx1,by1=P(9.3,-83.2)
o.append(f'<rect x="{bx0:.0f}" y="{by0:.0f}" width="{bx1-bx0:.0f}" height="{by1-by0:.0f}" fill="none" class="frame" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>')
o.append(f'<text x="{bx1+6:.0f}" y="{by0+10:.0f}" class="ink2 t-date halo">see inset, top right</text>')
# Central America inset (Pacific, lower-left)
ILON0, ILON1, ILAT0, ILAT1 = -89.7, -81.8, 9.25, 16.3
IH_T = 262; IK = math.cos(math.radians(13)); ISX = IH_T/(ILAT1-ILAT0); IH = IH_T; IW = int((ILON1-ILON0)*IK*ISX)
IX0 = W - IW - 14; IY0 = TOP + 40
def PI(lat, lon): return (IX0 + (lon-ILON0)*IK*ISX, IY0 + (ILAT1-lat)*ISX)
o.append(f'<line x1="{bx1:.0f}" y1="{(by0+by1)/2:.0f}" x2="{IX0-1:.0f}" y2="{IY0+IH/2:.0f}" class="frame" stroke-width="1" stroke-dasharray="4 3"/>')
o.append(f'<rect x="{IX0-1}" y="{IY0-30}" width="{IW+2}" height="{IH+31:.0f}" rx="6" class="box" stroke-width="1.2"/>')
o.append(f'<rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}" class="surface"/>')
o.append(f'<text x="{IX0+10}" y="{IY0-10}" class="ink t-stop">Central America, ≈ late Feb – Mar</text>')
o.append(f'<clipPath id="inset"><rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}"/></clipPath><g clip-path="url(#inset)">')
for name,d in land_paths(PI,(ILON0,ILON1,ILAT0,ILAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
for name,la,lo in [('HONDURAS',14.6,-86.6),('NICARAGUA',13.2,-85.0),('COSTA RICA',9.7,-83.75),('EL SALVADOR',13.6,-88.75)]:
    x,y=PI(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-date" text-anchor="middle" letter-spacing="1.5">{name}</text>')
draw_legs(o, PI, CAL)
draw_legs(o, PI, CAL_OPT, op=0.35)
ISTOP={35:(10,6,'start'),36:(10,-6,'start'),37:(-10,14,'end'),38:(-10,4,'end'),39:(-10,0,'end'),40:(10,8,'start'),41:(10,2,'start'),42:(-10,4,'end'),43:(10,16,'start'),44:(10,5,'start')}
for s_ in S:
    if s_[1] in CA:
        dx,dy,anc=ISTOP[s_[0]]; short=s_[1].split(' (')[0].split(' / ')[0].split(' +')[0]
        draw_stop(o, PI, s_[:2]+(s_[2],)+s_[3:5]+(dx,dy,anc), dates=False, r=7.5)
        o[-1]=o[-1].replace(f'>{s_[1]}</text>', f'>{short}' + (' (optional)' if s_[0] in OPTIONAL else '') + '</text>')
        if s_[0] in OPTIONAL: o[-1]=o[-1].replace('<g>','<g opacity="0.45">',1)
x,y=PI(*SAP); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"/><text x="{x+6:.0f}" y="{y-7:.0f}" class="ink2 t-date halo" opacity="0.6">San Pedro Sula ✈ home (if Honduras)</text>')
x,y=PI(*st['León'][3:5]); o.append(f'<text x="{x-10:.0f}" y="{y+18:.0f}" class="ink2 t-date halo" text-anchor="end">✈ home: Managua</text>')
x,y=PI(*SJO); o.append(f'<text x="{x+10:.0f}" y="{y+16:.0f}" class="ink2 t-date halo">✈ from Lima</text>')
o.append('</g>')
# title
o.append(f'<text x="32" y="40" class="ink t-title">Latin America draft route (Plan B): Rio → Uruguay → Paraguay → the Andes → Central America</text>')
o.append(f'<text x="32" y="64" class="ink2 t-sub">3 Dec 2026 → ≈ mid-Mar 2027 · Brazil dated from the checked itinerary · later dates ≈ pending decisions · faded = optional · dots nudged apart where crowded</text>')
# legend + itinerary list
ly=TOP+H_MAP+30; lx=32
o.append(f'<text x="{lx}" y="{ly}" class="ink t-stop">How each leg is travelled</text>')
for i,(k,v) in enumerate(MODES.items()):
    x0=lx+i*200; y0=ly+20; dash=f' stroke-dasharray="{v[2]}"' if v[2] else ''
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+44}" y2="{y0}" class="m-{k}" stroke-width="{v[3]+0.5}" stroke-linecap="round"{dash}/><text x="{x0+52}" y="{y0+4}" class="ink t-leg">{v[4]}</text>')
ty=ly+56; cols=[S[:15],S[15:30],S[30:]]
o.append(f'<text x="{lx}" y="{ty}" class="ink t-stop">Stops (≈ dates)</text>')
for ci,col in enumerate(cols):
    for ri,s_ in enumerate(col):
        x0=lx+ci*320; y0=ty+20+ri*17
        o.append(f'<text x="{x0}" y="{y0}" class="ink t-list"><tspan font-weight="700">{s_[0]}.</tspan> {s_[1]} <tspan class="ink2">{s_[2] or "≈ mid-Feb"}</tspan></text>')
o.append(f'<text x="{lx}" y="{ty+20+15*17+10}" class="ink2 t-note">Brazil (Dec) → Uruguay and Paraguay overland → ✈ Iguaçu–Santiago → over the Andes to Mendoza, Salta and the Atacama → Bolivia → Peru → ✈ Lima–San José → north.</text>')
o.append(f'<text x="{lx}" y="{ty+20+15*17+28}" class="ink2 t-note">Still to decide by ~10–15 Dec: trims vs dropping Honduras to finish by mid-March. Nazca is a daytime stop. Draft for planning, nothing booked.</text>')
o.append('</svg>')
open(OUT,'w').write('\n'.join(o)); print(OUT, W, H)
