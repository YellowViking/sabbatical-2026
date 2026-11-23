# LatAm draft route map (Dec 2026 – Mar 2027), same style as make_map.py. Usage:
#   curl -sLo /tmp/countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
#   python3 tools/route-map/latam_plan_map.py /tmp/countries.geojson trips/latam/latam-route-draft.svg
# Edit S (stops), L (legs by mode) and the Central America inset to redraw the plan.
import json, math, sys
GEO = sys.argv[1]; OUT = sys.argv[2]
LON0, LON1, LAT0, LAT1 = -95.0, -24.0, -36.5, 19.5
W = 1000; K = math.cos(math.radians(-8)); SX = W / ((LON1 - LON0) * K); H_MAP = (LAT1 - LAT0) * SX
TOP = 96; PAD_B = 350; H = int(TOP + H_MAP + PAD_B)
def P(lat, lon): return ((lon - LON0) * K * SX, TOP + (LAT1 - lat) * SX)

# --- stops: (n, name, dates, lat, lon, label dx, dy, anchor); CA=True → drawn in the inset
S = [
 (1,'São Paulo','4–6 Dec',-23.7,-47.0, -12,4,'end'),
 (2,'Jericoacoara','6–9 Dec',-2.79,-40.51, -12,-6,'end'),
 (3,'Canoa Quebrada','9–11 Dec',-4.53,-37.69, 12,-6,'start'),
 (4,'Pipa','11–14 Dec',-6.23,-35.05, 12,4,'start'),
 (5,'Olinda + Recife','14–16 Dec',-8.01,-34.86, 12,6,'start'),
 (6,'Salvador','16–19 Dec',-12.97,-38.5, 12,4,'start'),
 (7,'Chapada Diamantina','19–24 Dec',-12.56,-41.39, -12,-6,'end'),
 (8,'Rio de Janeiro','24–29 Dec',-22.7,-42.9, 12,-6,'start'),
 (9,'Ilha Grande','29–31 Dec',-23.8,-44.0, 12,12,'start'),
 (10,'Paraty','31 Dec–1 Jan',-23.1,-45.45, -2,28,'end'),
 (11,'Iguaçu Falls','1–3 Jan',-25.6,-54.5, -12,14,'end'),
 (12,'Santiago','3–6 Jan',-33.45,-70.67, 12,4,'start'),
 (13,'Valparaíso','6–8 Jan',-33.05,-71.62, -12,4,'end'),
 (14,'San Pedro de Atacama','8–11 Jan',-22.91,-68.2, -12,4,'end'),
 (15,'Uyuni','jeep tour 11–14 · 14–15 Jan',-20.8,-67.15, 12,12,'start'),
 (16,'Potosí','15–16 Jan',-19.95,-66.0, 12,10,'start'),
 (17,'Sucre','16–19 Jan',-18.75,-64.8, 12,-2,'start'),
 (18,'La Paz','19–23 Jan',-16.5,-68.15, 12,4,'start'),
 (19,'Copacabana + Isla del Sol','23–25 Jan',-16.0,-69.1, 8,-13,'start'),
 (20,'Puno','',-15.6,-70.1, -8,-10,'end'),
 (21,'Arequipa + Colca','26–30 Jan',-16.5,-71.6, -12,10,'end'),
 (22,'Huacachina','31 Jan–1 Feb',-14.4,-75.45, -12,14,'end'),
 (23,'Paracas','1–3 Feb',-13.55,-76.55, -12,2,'end'),
 (24,'Lima','3–4 Feb',-11.95,-77.1, -12,-4,'end'),
 (25,'San José','4–5 Feb',9.93,-84.08, 0,0,'start'),
 (26,'La Fortuna / Arenal','5–8 Feb',10.47,-84.64, 0,0,'start'),
 (27,'Monteverde','8–10 Feb',10.3,-84.82, 0,0,'start'),
 (28,'Rincón de la Vieja','10–12 Feb',10.77,-85.35, 0,0,'start'),
 (29,'Playa Maderas / SJDS','13–15 Feb',11.3,-85.87, 0,0,'start'),
 (30,'Ometepe','15–18 Feb',11.5,-85.6, 0,0,'start'),
 (31,'Granada + Apoyo + Masaya','18–21 Feb',11.93,-85.96, 0,0,'start'),
 (32,'León','21–25 Feb',12.43,-86.88, 0,0,'start'),
 (33,'Copán Ruinas','26–28 Feb',14.84,-89.14, 0,0,'start'),
 (34,'Utila (via La Ceiba)','1–6 Mar',16.1,-86.93, 0,0,'start'),
]
CA = {s[1] for s in S if s[0] >= 25}
st = {s[1]: s for s in S}
FOR, NAT, CJC, NAZ, ARA, LCE, SAP, SJO = (-3.73,-38.52), (-5.79,-35.21), (-22.46,-68.92), (-14.83,-74.94), (-4.56,-37.77), (15.76,-86.79), (15.5,-88.03), (9.93,-84.08)
LAG = (-22.2,-67.8); SALAR = (-20.2,-67.6)   # Laguna Colorada, salt flat (jeep-tour route)
L = [
 ('flight',['São Paulo','Jericoacoara']),
 ('bus',['Jericoacoara',FOR,'Canoa Quebrada',NAT,'Pipa','Olinda + Recife']),
 ('flight',['Olinda + Recife','Salvador']),
 ('bus',['Salvador','Chapada Diamantina']),
 ('flight',['Salvador','Rio de Janeiro']),
 ('boat',['Rio de Janeiro','Ilha Grande','Paraty']),
 ('bus',['Paraty','São Paulo']),
 ('flight',['São Paulo','Iguaçu Falls']),
 ('flight',['Iguaçu Falls','Santiago']),
 ('bus',['Santiago','Valparaíso']),
 ('flight',['Santiago',CJC]),
 ('bus',[CJC,'San Pedro de Atacama']),
 ('jeep',['San Pedro de Atacama',LAG,SALAR,'Uyuni']),
 ('bus',['Uyuni','Potosí','Sucre','La Paz','Copacabana + Isla del Sol','Puno','Arequipa + Colca',NAZ,'Huacachina','Paracas','Lima']),
 ('flight',['Lima',SJO]),
]
# Central America inset legs (drawn only in the inset)
FORT_LAKE = (10.5,-84.85); LIB = (10.63,-85.44); SJORGE = (11.43,-85.84); LCEIBA = LCE
CAL = [
 ('bus',['San José','La Fortuna / Arenal']),
 ('boat',['La Fortuna / Arenal',FORT_LAKE]),
 ('bus',[FORT_LAKE,'Monteverde',LIB,'Rincón de la Vieja','Playa Maderas / SJDS',SJORGE]),
 ('boat',[SJORGE,'Ometepe']),
 ('bus',['Ometepe','Granada + Apoyo + Masaya','León','Copán Ruinas',SAP,LCEIBA]),
 ('boat',[LCEIBA,'Utila (via La Ceiba)']),
]
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
def draw_legs(o, proj, legs):
    for mode,items in legs:
        c=MODES[mode]; dash=f' stroke-dasharray="{c[2]}"' if c[2] else ''; d=path(mode,items,proj)
        o.append(f'<path class="ring" d="{d}" fill="none" stroke-width="{c[3]+3}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
        o.append(f'<path class="m-{mode}" d="{d}" fill="none" stroke-width="{c[3]}" stroke-linecap="round" stroke-linejoin="round"{dash}><title>{c[4]}</title></path>')
def draw_stop(o, proj, s, label=True, dates=True, r=8.5):
    n,name,dt,la,lo,dx,dy,anc=s; x,y=proj(la,lo)
    o.append(f'<g><title>{n}. {name}: {dt}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="dot ring" stroke-width="2"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" class="num t-num" text-anchor="middle">{n}</text>'
             + (f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="ink t-stop halo" text-anchor="{anc}">{name}'
                + (f' <tspan class="ink2 t-date">{dt}</tspan>' if dates else '') + '</text>' if label else '') + '</g>')

o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, -apple-system, \'Segoe UI\', sans-serif">',
   '<title>Latin America draft route: São Paulo to Utila, 3 Dec 2026 – 7 Mar 2027</title>', f'<style>{CSS}</style>',
   f'<rect width="{W}" height="{H}" class="page"/>', f'<rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}" class="surface"/>',
   f'<clipPath id="map"><rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}"/></clipPath>','<g clip-path="url(#map)">']
for name,d in land_paths(P,(LON0,LON1,LAT0,LAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
for name,la,lo in [('BRAZIL',-10,-52),('BOLIVIA',-17.5,-63.5),('PERU',-9,-75),('CHILE',-29,-69.2),('ARGENTINA',-30,-63),('PARAGUAY',-23,-58.5)]:
    x,y=P(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-country" text-anchor="middle">{name}</text>')
o.append('</g>')
draw_legs(o, P, L)
# Central America on the main map: dots only, framed, pointing to the inset
for s_ in S:
    if s_[1] in CA:
        x,y=P(*s_[3:5]); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>{s_[0]}. {s_[1]}: {s_[2]}</title></circle>')
    else:
        draw_stop(o, P, s_)
# small waypoint dot: Nazca (no night)
x,y=P(*NAZ); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>Nazca: viewing tower stop, 31 Jan</title></circle>')
x,y=P(*st['Chapada Diamantina'][3:5]); o.append(f'<text x="{x-12:.0f}" y="{y+10:.0f}" class="ink2 t-date halo" text-anchor="end">bus there and back</text>')
# Seattle arrows
x,y=P(*st['São Paulo'][3:5]); o.append(f'<path class="m-flight" d="M{x-150:.0f},{y-250:.0f} Q{x-120:.0f},{y-80:.0f} {x-7:.0f},{y-4:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{x-150:.0f}" y="{y-256:.0f}" class="ink2 t-date halo" text-anchor="middle">✈ from Seattle, 3 Dec (Alaska award)</text>')
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
o.append(f'<text x="{IX0+10}" y="{IY0-10}" class="ink t-stop">Central America, 4 Feb – 7 Mar</text>')
o.append(f'<clipPath id="inset"><rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}"/></clipPath><g clip-path="url(#inset)">')
for name,d in land_paths(PI,(ILON0,ILON1,ILAT0,ILAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
for name,la,lo in [('HONDURAS',14.6,-86.6),('NICARAGUA',13.2,-85.0),('COSTA RICA',9.7,-83.75),('EL SALVADOR',13.6,-88.75)]:
    x,y=PI(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-date" text-anchor="middle" letter-spacing="1.5">{name}</text>')
draw_legs(o, PI, CAL)
ISTOP={25:(10,6,'start'),26:(10,-6,'start'),27:(-10,14,'end'),28:(-10,4,'end'),29:(-10,0,'end'),30:(10,8,'start'),31:(10,2,'start'),32:(-10,4,'end'),33:(10,16,'start'),34:(10,5,'start')}
for s_ in S:
    if s_[1] in CA:
        dx,dy,anc=ISTOP[s_[0]]; short=s_[1].split(' (')[0].split(' / ')[0].split(' +')[0]
        draw_stop(o, PI, s_[:2]+(s_[2],)+s_[3:5]+(dx,dy,anc), dates=False, r=7.5)
        o[-1]=o[-1].replace(f'>{s_[1]}</text>', f'>{short}</text>')
x,y=PI(*SAP); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"/><text x="{x+6:.0f}" y="{y-7:.0f}" class="ink2 t-date halo">San Pedro Sula ✈ home 7 Mar</text>')
x,y=PI(*SJO); o.append(f'<text x="{x+10:.0f}" y="{y+16:.0f}" class="ink2 t-date halo">✈ from Lima</text>')
o.append('</g>')
# title
o.append(f'<text x="32" y="40" class="ink t-title">Latin America draft route (option 1): São Paulo → Utila</text>')
o.append(f'<text x="32" y="64" class="ink2 t-sub">≈ 3 Dec 2026 – 7 Mar 2027 · 34 stops · typical backpacker days · ~8 buffer days left before 15 Mar · draft, not booked · dots nudged apart where crowded</text>')
# legend + itinerary list
ly=TOP+H_MAP+30; lx=32
o.append(f'<text x="{lx}" y="{ly}" class="ink t-stop">How each leg is travelled</text>')
for i,(k,v) in enumerate(MODES.items()):
    x0=lx+i*200; y0=ly+20; dash=f' stroke-dasharray="{v[2]}"' if v[2] else ''
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+44}" y2="{y0}" class="m-{k}" stroke-width="{v[3]+0.5}" stroke-linecap="round"{dash}/><text x="{x0+52}" y="{y0+4}" class="ink t-leg">{v[4]}</text>')
ty=ly+56; cols=[S[:12],S[12:24],S[24:]]
o.append(f'<text x="{lx}" y="{ty}" class="ink t-stop">Stops (≈ dates)</text>')
for ci,col in enumerate(cols):
    for ri,s_ in enumerate(col):
        x0=lx+ci*320; y0=ty+20+ri*17
        o.append(f'<text x="{x0}" y="{y0}" class="ink t-list"><tspan font-weight="700">{s_[0]}.</tspan> {s_[1]} <tspan class="ink2">{s_[2] or "25–26 Jan"}</tspan></text>')
o.append(f'<text x="{lx}" y="{ty+20+12*17+10}" class="ink2 t-note">Brazil north → south in Dec · Chile → Bolivia → Peru northward in Jan · Central America south → north in Feb–Mar.</text>')
o.append(f'<text x="{lx}" y="{ty+20+12*17+28}" class="ink2 t-note">Nazca (31 Jan) is a daytime stop. Hikes per country are kept in a separate backlog. Draft for planning, nothing booked.</text>')
o.append('</svg>')
open(OUT,'w').write('\n'.join(o)); print(OUT, W, H)
