# LatAm draft route map (Dec 2026 – Mar 2027), same style as make_map.py. Usage:
#   curl -sLo /tmp/countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
#   python3 tools/route-map/latam_plan_map.py /tmp/countries.geojson trips/latam/latam-route-draft.svg
# Edit S (stops), L (legs by mode) and the Central America inset to redraw the plan.
# Each stop links to its guide on the latam-route-v5 branch; after merging, set GUIDE_BASE=…/blob/main/trips/latam/ and redraw.
import json, math, sys, os
GEO = sys.argv[1]; OUT = sys.argv[2]
LON0, LON1, LAT0, LAT1 = -95.0, -24.0, -36.5, 19.5
W = 1000; K = math.cos(math.radians(-8)); SX = W / ((LON1 - LON0) * K); H_MAP = (LAT1 - LAT0) * SX
TOP = 96; PAD_B = 400; H = int(TOP + H_MAP + PAD_B)
def P(lat, lon): return ((lon - LON0) * K * SX, TOP + (LAT1 - lat) * SX)

# --- stops: (n, name, dates, lat, lon, label dx, dy, anchor); CA=True → drawn in the inset
S = [
 (1,'Rio de Janeiro','8–12 Dec',-22.7,-42.9, 12,-6,'start'),
 (2,'Ilha Grande','12–14 Dec',-23.8,-44.0, 12,12,'start'),
 (3,'Paraty','14–15 Dec',-23.1,-45.45, -2,-14,'end'),
 (4,'São Paulo','15–17 Dec',-23.7,-47.0, -12,-6,'end'),
 (5,'Curitiba','17–18 Dec',-25.43,-49.27, 12,14,'start'),
 (6,'Foz do Iguaçu','19–21 Dec',-25.55,-54.58, 10,18,'start'),
 (7,'Asunción','21–23 Dec',-25.28,-57.63, -10,-10,'end'),
 (8,'Encarnación','23–26 Dec',-27.33,-55.87, 12,10,'start'),
 (9,'Montevideo','27–28 Dec · 30 Dec–1 Jan',-34.9,-56.16, 4,22,'start'),
 (10,'Cabo Polonio','28–30 Dec',-34.4,-53.78, 12,-4,'start'),
 (11,'Colonia (stopover)','1 Jan',-34.47,-57.84, -12,-8,'end'),
 (12,'Córdoba + Los Gigantes','2–7 Jan',-31.42,-64.18, -12,4,'end'),
 (13,'Cafayate','8–10 Jan',-26.07,-65.98, -12,6,'end'),
 (14,'Salta','10–12 Jan',-24.79,-65.41, 12,6,'start'),
 (15,'Tilcara + Iruya + Purmamarca','12–15 Jan',-23.6,-65.4, 12,-2,'start'),
 (16,'San Pedro de Atacama','15–18 Jan',-22.91,-68.2, -12,6,'end'),
 (17,'Uyuni','jeep tour 18–20 Jan',-20.46,-66.83, -12,8,'end'),
 (18,'Potosí','20–22 Jan',-19.95,-66.0, 12,10,'start'),
 (19,'Sucre','22–25 Jan',-18.75,-64.8, 12,-2,'start'),
 (20,'La Paz','25–28 Jan',-16.5,-68.15, 12,4,'start'),
 (21,'Isla del Sol','28–29 Jan',-16.0,-69.1, 8,-13,'start'),
 (22,'Puno','29–30 Jan',-15.6,-70.1, 0,-14,'middle'),
 (23,'Colca (Chivay, Sangalle)','30 Jan–1 Feb',-15.4,-72.1, -12,-4,'end'),
 (24,'Arequipa','1–3 Feb',-16.7,-71.4, -12,12,'end'),
 (25,'Panama City','3–5 Feb',8.98,-79.52, 0,0,'start'),
 (26,'Boquete','5–8 Feb',8.78,-82.43, 0,0,'start'),
 (27,'San Gerardo de Rivas (Chirripó)','8–11 Feb',9.47,-83.58, 0,0,'start'),
 (28,'Uvita','11–13 Feb',9.16,-83.74, 0,0,'start'),
 (29,'Monteverde','13–15 Feb',10.3,-84.82, 0,0,'start'),
 (30,'La Fortuna / Arenal','15–18 Feb',10.47,-84.64, 0,0,'start'),
 (31,'Rincón de la Vieja (Liberia)','18–20 Feb',10.77,-85.35, 0,0,'start'),
 (32,'San Juan del Sur / Playa Maderas','20–22 Feb',11.25,-85.87, 0,0,'start'),
 (33,'Ometepe','22–25 Feb',11.5,-85.6, 0,0,'start'),
 (34,'Granada + Laguna de Apoyo','25–27 Feb',11.93,-85.96, 0,0,'start'),
 (35,'León','27 Feb–2 Mar',12.43,-86.88, 0,0,'start'),
 (36,'Estelí','2–3 Mar (+ airport night)',13.09,-86.35, 0,0,'start'),
 (37,'Somoto canyon','optional',13.48,-86.58, 0,0,'start'),
]
OPTIONAL = {37}
# each stop links to its guide when the SVG is opened on its own (GitHub shows embedded SVGs as plain images)
GUIDE_BASE = os.environ.get('GUIDE_BASE', 'https://github.com/YellowViking/sabbatical-2026/blob/latam-route-v5/trips/latam/')
GUIDES = dict(enumerate(['rio-de-janeiro','ilha-grande','paraty','sao-paulo','curitiba','foz-do-iguacu','asuncion','encarnacion','montevideo','cabo-polonio','colonia',
  'cordoba','cafayate','salta','quebrada-de-humahuaca','san-pedro-de-atacama','uyuni-jeep-tour','potosi','sucre','la-paz','copacabana-isla-del-sol','puno','colca-canyon',
  'arequipa','panama-city','boquete','san-gerardo-de-rivas','uvita','monteverde','la-fortuna','rincon-de-la-vieja','san-juan-del-sur','ometepe','granada','leon','esteli','somoto'], 1))
def gurl(page): return GUIDE_BASE + page if page.endswith('.md') or '#' in page else GUIDE_BASE + 'guides/' + page + '.md'
def alink(page, inner): return f'<a href="{gurl(page)}" xlink:href="{gurl(page)}" target="_top">{inner}</a>'
CA = {s[1] for s in S if s[0] >= 25}
st = {s[1]: s for s in S}
FOR, NAT, GOI, POA, CHUY, BA, POS, CDE = (-3.73,-38.52), (-5.79,-35.21), (-6.27,-35.21), (-30.03,-51.23), (-33.69,-53.46), (-34.6,-58.38), (-27.37,-55.9), (-25.51,-54.61)
TUC, JAMA, NAZ, SJO = (-26.82,-65.22), (-23.24,-67.03), (-14.83,-74.94), (9.93,-84.08)
LAG = (-22.2,-67.8); SALAR = (-20.2,-67.6); IRUYA = (-22.79,-65.21); MGA = (12.14,-86.17)
CONC, SALTO_UY, JUJ, LIMA, PTY = (-31.39,-58.02), (-31.38,-57.96), (-24.19,-65.3), (-12.02,-77.11), (8.98,-79.52)
L = [
 ('boat',['Rio de Janeiro','Ilha Grande','Paraty']),
 ('bus',['Paraty','São Paulo','Curitiba','Foz do Iguaçu',CDE,'Asunción','Encarnación',POS,CONC,'Montevideo']),
 ('bus',['Montevideo','Cabo Polonio']),
 ('bus',['Montevideo','Colonia (stopover)']),
 ('boat',['Colonia (stopover)',BA]),
 ('bus',[BA,'Córdoba + Los Gigantes',TUC,'Cafayate','Salta',JUJ,'Tilcara + Iruya + Purmamarca',IRUYA,'Tilcara + Iruya + Purmamarca',JAMA,'San Pedro de Atacama']),
 ('jeep',['San Pedro de Atacama',LAG,SALAR,'Uyuni']),
 ('bus',['Uyuni','Potosí','Sucre']),
 ('flight',['Sucre','La Paz']),
 ('bus',['La Paz','Isla del Sol','Puno','Colca (Chivay, Sangalle)','Arequipa']),
 ('flight',['Arequipa',LIMA]),
 ('flight',[LIMA,PTY]),
]
FORT_LAKE = (10.5,-84.85); LIB = (10.63,-85.44); SJORGE = (11.43,-85.84); DAVID = (8.43,-82.43); PCANOAS = (8.54,-82.84); SISIDRO = (9.37,-83.70)
QUEPOS = (9.43,-84.16); PUNTA = (9.98,-84.83); PBLANCAS = (11.21,-85.61); ESTELI = (13.09,-86.35)
CAL = [
 ('flight',['Panama City',DAVID]), ('bus',[DAVID,'Boquete']),
 ('bus',['Boquete',DAVID,PCANOAS,SISIDRO,'San Gerardo de Rivas (Chirripó)']),
 ('bus',['San Gerardo de Rivas (Chirripó)',SISIDRO,'Uvita',QUEPOS,PUNTA,'Monteverde']),
 ('bus',['Monteverde',FORT_LAKE]), ('boat',[FORT_LAKE,(10.52,-84.75)]), ('bus',[(10.52,-84.75),'La Fortuna / Arenal']),
 ('bus',['La Fortuna / Arenal','Rincón de la Vieja (Liberia)',PBLANCAS,'San Juan del Sur / Playa Maderas',SJORGE]),
 ('boat',[SJORGE,'Ometepe']),
 ('bus',[SJORGE,'Granada + Laguna de Apoyo','León','Estelí',MGA]),
]
CAL_OPT = [('bus',['Estelí','Somoto canyon'])]
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
  a { cursor: pointer; } a:hover .t-stop, a:hover .t-list, a:hover .t-date, a:hover .t-leg { text-decoration: underline; } a:hover circle { stroke-width: 3.5px; }
"""
def draw_legs(o, proj, legs, op=1.0):
    for mode,items in legs:
        c=MODES[mode]; dash=f' stroke-dasharray="{c[2]}"' if c[2] else ''; d=path(mode,items,proj)
        o.append(f'<path class="ring" d="{d}" fill="none" stroke-width="{c[3]+3}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
        o.append(f'<path class="m-{mode}" d="{d}" fill="none" stroke-width="{c[3]}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"{dash}><title>{c[4]}</title></path>')
def draw_stop(o, proj, s, label=True, dates=True, r=8.5):
    n,name,dt,la,lo,dx,dy,anc=s; x,y=proj(la,lo)
    g=(f'<g><title>{n}. {name}: {dt} (click for the guide)</title><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="dot ring" stroke-width="2"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" class="num t-num" text-anchor="middle">{n}</text>'
             + (f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="ink t-stop halo" text-anchor="{anc}">{name}'
                + (f' <tspan class="ink2 t-date">{dt}</tspan>' if dates else '') + '</text>' if label else '') + '</g>')
    o.append(alink(GUIDES[n], g) if n in GUIDES else g)

o=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, -apple-system, \'Segoe UI\', sans-serif">',
   '<title>Latin America route v5: Rio → Iguaçu → Paraguay → Uruguay → NW Argentina → Atacama → Bolivia → Peru → Panama → Costa Rica → Nicaragua</title>', f'<style>{CSS}</style>',
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
        draw_stop(o, P, s_, dates=False)
        if s_[0] == 15: o[-1]=o[-1].replace('>Tilcara + Iruya + Purmamarca</text>','>Quebrada</text>')
x,y=P(*st['Cabo Polonio'][3:5]); o.append(f'<text x="{x+12:.0f}" y="{y+10:.0f}" class="ink2 t-date halo">there and back from Montevideo</text>')
x,y=P(*LIMA); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>Lima: change planes</title></circle><text x="{x-8:.0f}" y="{y+4:.0f}" class="ink2 t-date halo" text-anchor="end">Lima (change planes)</text>')
# Seattle arrows
x,y=P(*st['Rio de Janeiro'][3:5]); o.append(f'<path class="m-flight" d="M{x-170:.0f},{y-250:.0f} Q{x-110:.0f},{y-90:.0f} {x-6:.0f},{y-6:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{x-170:.0f}" y="{y-256:.0f}" class="ink2 t-date halo" text-anchor="middle">✈ from Seattle, Mon 7 Dec (Alaska award, business)</text>')
for nm,(la,lo),dx,dy,anc in [('Buenos Aires (ferry, then night bus)',BA,-10,20,'end')]:
    x,y=P(la,lo); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>{nm}</title></circle><text x="{x+dx:.0f}" y="{y+dy:.0f}" class="ink2 t-date halo" text-anchor="{anc}">{nm}</text>')
bx0,by0=P(13.9,-88.6); bx1,by1=P(7.7,-79.0)
o.append(f'<rect x="{bx0:.0f}" y="{by0:.0f}" width="{bx1-bx0:.0f}" height="{by1-by0:.0f}" fill="none" class="frame" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>')
o.append(f'<text x="{bx1+6:.0f}" y="{by0+10:.0f}" class="ink2 t-date halo">see inset, top right</text>')
# Central America inset (Pacific, lower-left)
ILON0, ILON1, ILAT0, ILAT1 = -88.6, -79.0, 7.7, 13.9
IH_T = 262; IK = math.cos(math.radians(11)); ISX = IH_T/(ILAT1-ILAT0); IH = IH_T; IW = int((ILON1-ILON0)*IK*ISX)
IX0 = W - IW - 14; IY0 = TOP + 40
def PI(lat, lon): return (IX0 + (lon-ILON0)*IK*ISX, IY0 + (ILAT1-lat)*ISX)
o.append(f'<line x1="{bx1:.0f}" y1="{(by0+by1)/2:.0f}" x2="{IX0-1:.0f}" y2="{IY0+IH/2:.0f}" class="frame" stroke-width="1" stroke-dasharray="4 3"/>')
o.append(f'<rect x="{IX0-1}" y="{IY0-30}" width="{IW+2}" height="{IH+31:.0f}" rx="6" class="box" stroke-width="1.2"/>')
o.append(f'<rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}" class="surface"/>')
o.append(f'<text x="{IX0+10}" y="{IY0-10}" class="ink t-stop">Central America, 3 Feb – 4 Mar</text>')
o.append(f'<clipPath id="inset"><rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}"/></clipPath><g clip-path="url(#inset)">')
for name,d in land_paths(PI,(ILON0,ILON1,ILAT0,ILAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
for name,la,lo in [('HONDURAS',13.75,-86.0),('NICARAGUA',12.9,-85.0),('COSTA RICA',10.05,-83.6),('PANAMA',7.95,-80.2)]:
    x,y=PI(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-date" text-anchor="middle" letter-spacing="1.5">{name}</text>')
draw_legs(o, PI, CAL)
draw_legs(o, PI, CAL_OPT, op=0.35)
ISTOP={25:(-10,-9,'end'),26:(10,8,'start'),27:(10,-4,'start'),28:(-10,10,'end'),29:(-10,4,'end'),30:(10,-6,'start'),31:(-10,-4,'end'),32:(-10,-2,'end'),33:(10,8,'start'),34:(10,2,'start'),35:(-10,4,'end'),36:(10,-2,'start'),37:(10,4,'start')}
for s_ in S:
    if s_[1] in CA:
        dx,dy,anc=ISTOP[s_[0]]; short=s_[1].split(' (')[0].split(' / ')[0].split(' +')[0]
        draw_stop(o, PI, s_[:2]+(s_[2],)+s_[3:5]+(dx,dy,anc), dates=False, r=7.5)
        o[-1]=o[-1].replace(f'>{s_[1]}</text>', f'>{short}' + (' (optional)' if s_[0] in OPTIONAL else '') + '</text>')
        if s_[0] in OPTIONAL: o[-1]=o[-1].replace('<g>','<g opacity="0.45">',1)
        if s_[0] == 25: o[-1]=o[-1].replace('>Panama City</text>','>Panama City <tspan class="ink2 t-date">✈ from Lima</tspan></text>')
x,y=PI(*MGA); o.append(alink('flight-home', f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"/><text x="{x+10:.0f}" y="{y-12:.0f}" class="ink2 t-date halo">✈ home from Managua, Thu 4 Mar</text>'))

o.append('</g>')
# title
o.append(f'<text x="32" y="40" class="ink t-title">Latin America route v5: Rio → Paraguay → Uruguay → the Andes → Central America</text>')
o.append(f'<text x="32" y="64" class="ink2 t-sub">✈ Mon 7 Dec 2026 → ✈ home Thu 4 Mar 2027 · 11 spare days · faded = optional · dots nudged apart where crowded · nothing booked</text>')
# legend + itinerary list
ly=TOP+H_MAP+30; lx=32
o.append(f'<text x="{lx}" y="{ly}" class="ink t-stop">How each leg is travelled</text>')
for i,(k,v) in enumerate(MODES.items()):
    x0=lx+i*200; y0=ly+20; dash=f' stroke-dasharray="{v[2]}"' if v[2] else ''
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+44}" y2="{y0}" class="m-{k}" stroke-width="{v[3]+0.5}" stroke-linecap="round"{dash}/><text x="{x0+52}" y="{y0+4}" class="ink t-leg">{v[4]}</text>')
ty=ly+56; cols=[S[:13],S[13:26],S[26:]]
o.append(f'<text x="{lx}" y="{ty}" class="ink t-stop">Stops (≈ dates)</text>')
for ci,col in enumerate(cols):
    for ri,s_ in enumerate(col):
        x0=lx+ci*320; y0=ty+20+ri*17
        o.append(alink(GUIDES[s_[0]], f'<text x="{x0}" y="{y0}" class="ink t-list"><tspan font-weight="700">{s_[0]}.</tspan> {s_[1]} <tspan class="ink2">{s_[2] or "≈ mid-Feb"}</tspan></text>'))
o.append(f'<text x="{lx}" y="{ty+20+13*17+10}" class="ink2 t-note">Overland everywhere except ✈ Sucre → La Paz, ✈ Arequipa → Lima → Panama City and ✈ Panama City → David (Boquete, Carnaval).</text>')
o.append(f'<text x="{lx}" y="{ty+20+13*17+28}" class="ink2 t-note">Night buses: Curitiba → Foz, Encarnación → Montevideo, Buenos Aires → Córdoba, Córdoba → Tucumán. Only spurs: Cabo Polonio and the Ometepe ferry.</text>')
o.append(f'<text x="{lx}" y="{ty+20+13*17+46}" class="ink2 t-note">Beds, buses and flights checked live 24–26 Nov (see itinerary.md). Click a stop for its guide. Options and add-ons are in alternatives.md and its map. Nothing booked.</text>')
o.append('</svg>')
open(OUT,'w').write('\n'.join(o)); print(OUT, W, H)
