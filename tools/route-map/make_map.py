# Route map generator (Europe 2026 example). Usage:
#   curl -sLo /tmp/countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
#   python3 tools/route-map/make_map.py /tmp/countries.geojson trips/europe-2026/europe-route.svg
# Edit S (stops), L (legs by mode), the map bounds and the inset to draw another trip.
import json, math, sys
GEO = sys.argv[1]; OUT = sys.argv[2]
LON0, LON1, LAT0, LAT1 = 0.0, 28.5, 35.8, 63.6
W = 1000; K = math.cos(math.radians(50)); SX = W / ((LON1 - LON0) * K); H_MAP = (LAT1 - LAT0) * SX
TOP = 96; PAD_B = 150; H = int(TOP + H_MAP + PAD_B)
def P(lat, lon): return ((lon - LON0) * K * SX, TOP + (LAT1 - lat) * SX)

# --- stops: (n, name, dates, lat, lon, label dx, dy, anchor)
S = [
 (1,'Copenhagen','24–≈28 Aug',55.676,12.568, 12,4,'start'),
 (2,'Gothenburg','late Aug',57.709,11.974, 12,4,'start'),
 (3,'Oslo','to 2 Sep',59.911,10.75, 12,-2,'start'),
 (4,'Stavanger','2–6 Sep',58.97,5.733, -12,4,'end'),
 (5,'Bergen','6–8 · 13–19 Sep',60.39,5.32, -12,4,'end'),
 (6,'Stockholm','8–13 Sep',59.33,18.07, 12,4,'start'),
 (7,'Riga','19 Sep → · 3 Oct',56.95,24.105, -12,4,'end'),
 (8,'Tallinn','late Sep',59.437,24.754, 12,6,'start'),
 (9,'Helsinki','late Sep',60.17,24.94, 12,4,'start'),
 (10,'Vilnius','3–6 Oct',54.687,25.28, 12,4,'start'),
 (11,'Białystok','6–7 Oct',53.13,23.16, 12,4,'start'),
 (12,'Wrocław','7–10 Oct',51.108,17.04, 12,4,'start'),
 (13,'Prague','10–12 Oct',50.088,14.42, -12,4,'end'),
 (14,'Brno','12–13 Oct',49.195,16.608, 12,4,'start'),
 (15,'Graz','13–14 Oct',47.07,15.44, 12,4,'start'),
 (16,'Zagreb + Plitvice','14–16 Oct',45.815,15.98, 12,4,'start'),
 (17,'Bled (Lesce)','16–20 Oct',46.36,14.15, -12,-4,'end'),
 (18,'Ljubljana','20–22 Oct',46.056,14.506, -10,20,'end'),
 (19,'Padua','22–26 Oct · Venice, Verona',45.408,11.876, -12,4,'end'),
 (20,'Bologna','26–27 Oct',44.494,11.343, 12,4,'start'),
 (21,'Florence','27–30 Oct · Siena',43.769,11.256, 12,6,'start'),
 (22,'Cinque Terre','30 Oct–2 Nov',44.10,9.82, -12,4,'end'),
 (23,'Naples','≈2–9 Nov · Pompeii, Amalfi',40.852,14.268, -12,4,'end'),
 (24,'Reggio Calabria','≈9–11 Nov',38.11,15.65, 12,4,'start'),
 (25,'Catania','11–14 Nov',37.50,15.09, 12,10,'start'),
 (26,'Syracuse','13 Nov day trip',37.07,15.29, 12,4,'start'),
 (27,'Taormina','14–16 Nov',37.82,15.27, 12,-4,'start'),
 (28,'Cefalù','16 Nov stop',38.04,14.02, -4,-14,'middle'),
 (29,'Palermo','16–20 Nov',38.116,13.36, -12,4,'end'),
]
st = {s[1]: s for s in S}
SIC = {'Reggio Calabria','Catania','Syracuse','Taormina','Cefalù','Palermo'}
ILON0, ILON1, ILAT0, ILAT1 = 12.95, 16.75, 36.6, 38.75
IW = 400; IK = math.cos(math.radians(37.8)); ISX = IW/((ILON1-ILON0)*IK); IH = (ILAT1-ILAT0)*ISX
IX0 = W-IW-24; IY0 = 0  # set after TOP known
def pt(name): s = st[name]; return P(s[3], s[4])
# --- legs: (mode, [stop names or (lat,lon)])
FJ = [(60.07,6.55),(60.47,7.07),(60.63,6.42),(61.1,7.48),(62.1,7.2),(61.37,6.0)]  # Odda, Eidfjord, Voss, Laerdal, Geiranger, Gaularfjellet
L = [
 ('train',['Copenhagen','Gothenburg','Oslo','Stavanger']),
 ('bus',['Stavanger','Bergen']),
 ('flight',['Bergen','Stockholm']),
 ('car',['Bergen']+FJ+['Bergen']),
 ('flight',['Bergen','Riga']),
 ('train',['Riga','Tallinn']),
 ('ferry',['Tallinn','Helsinki']),
 ('bus',['Riga','Vilnius']),
 ('train',['Vilnius','Białystok','Wrocław','Prague','Brno','Graz']),
 ('bus',['Graz','Zagreb + Plitvice']),
 ('train',['Zagreb + Plitvice','Ljubljana','Bled (Lesce)']),
 ('train',['Bled (Lesce)','Ljubljana']),
 ('bus',['Ljubljana',(45.65,13.77)]),
 ('train',[(45.65,13.77),'Padua','Bologna','Florence','Cinque Terre']),
 ('train',['Cinque Terre',(43.72,10.40),(41.90,12.50),'Naples']),
 ('train',['Naples',(38.22,15.64)]),
 ('ferry',[(38.22,15.64),(38.19,15.55)]),
 ('train',[(38.19,15.55),'Catania']),
 ('train',['Catania','Syracuse']),
 ('train',['Catania','Taormina',(38.19,15.55),'Cefalù','Palermo']),
]
MODES = {  # light, dark, dash, width, label
 'train': ('#2a78d6','#3987e5','',3,'Train'),
 'bus':   ('#eb6834','#d95926','9 5',3,'Bus'),
 'flight':('#1baf7a','#199e70','2 6',2.5,'Flight'),
 'ferry': ('#eda100','#c98500','1 4',3,'Ferry'),
 'car':   ('#e87ba4','#d55181','10 4 2 4',2.5,'Road trip (car)'),
}

def path(mode, items, proj):
    ps=[proj(*(st[i][3:5] if isinstance(i,str) else i)) for i in items]
    if mode=='flight':
        (x1,y1),(x2,y2)=ps; mx,my=(x1+x2)/2,(y1+y2)/2; dx,dy=x2-x1,y2-y1; nx,ny=-dy,dx; n=math.hypot(nx,ny) or 1
        bend=0.18*math.hypot(dx,dy); cx,cy=mx+nx/n*bend*(-1 if ny>0 else 1),my+ny/n*bend*(-1 if ny>0 else 1)
        return f'M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}'
    return 'M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in ps)

# --- inset placement (bottom-right, over the Balkans/Greece area)
IY0 = TOP + H_MAP - IH - 24
def PI(lat, lon): return (IX0 + (lon-ILON0)*IK*ISX, IY0 + (ILAT1-lat)*ISX)
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
  .ink { fill: #0b0b0b; } .ink2 { fill: #52514e; } .halo { stroke: #fcfcfb; } .frame { stroke: #52514e; }
  .ring { stroke: #fcfcfb; } .dot { fill: #0b0b0b; } .num { fill: #fcfcfb; }
""" + ''.join(f"  .m-{k} {{ stroke: {v[0]}; }} .mf-{k} {{ fill: {v[0]}; }}\n" for k,v in MODES.items()) + """
  @media (prefers-color-scheme: dark) {
    .surface { fill: #0f1418; } .page { fill: #1a1a19; } .land { fill: #1a1a19; stroke: #383835; }
    .ink { fill: #f0efec; } .ink2 { fill: #c3c2b7; } .halo { stroke: #1a1a19; } .frame { stroke: #c3c2b7; }
    .ring { stroke: #1a1a19; } .dot { fill: #f0efec; } .num { fill: #1a1a19; }
""" + ''.join(f"    .m-{k} {{ stroke: {v[1]}; }} .mf-{k} {{ fill: {v[1]}; }}\n" for k,v in MODES.items()) + """  }
  .t-title { font-size: 22px; font-weight: 700; } .t-sub { font-size: 13px; }
  .t-stop { font-size: 13px; font-weight: 650; } .t-date { font-size: 11px; font-weight: 400; }
  .t-num { font-size: 10px; font-weight: 700; } .t-leg { font-size: 12.5px; } .t-note { font-size: 11.5px; }
  .halo { stroke-width: 3.5px; stroke-linejoin: round; paint-order: stroke; }
"""
def draw_legs(o, proj, legs, scale=1.0):
    for mode,items in legs:
        c=MODES[mode]; dash=f' stroke-dasharray="{c[2]}"' if c[2] else ''; d=path(mode,items,proj)
        o.append(f'<path class="ring" d="{d}" fill="none" stroke-width="{c[3]+3}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9"/>')
        o.append(f'<path class="m-{mode}" d="{d}" fill="none" stroke-width="{c[3]}" stroke-linecap="round" stroke-linejoin="round"{dash}><title>{c[4]}</title></path>')
def draw_stop(o, proj, s, label=True):
    n,name,dates,la,lo,dx,dy,anc=s; x,y=proj(la,lo)
    o.append(f'<g><title>{n}. {name}: {dates}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="8.5" class="dot ring" stroke-width="2"/>'
             f'<text x="{x:.1f}" y="{y+3.4:.1f}" class="num t-num" text-anchor="middle">{n}</text>'
             + (f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="ink t-stop halo" text-anchor="{anc}">{name} <tspan class="ink2 t-date">{dates}</tspan></text>' if label else '') + '</g>')
o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="system-ui, -apple-system, \'Segoe UI\', sans-serif">',
   '<title>Europe 2026 route: Copenhagen to Palermo, 24 Aug – 20 Nov 2026</title>',f'<style>{CSS}</style>',
   f'<rect width="{W}" height="{H}" class="page"/>', f'<rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}" class="surface"/>',
   f'<clipPath id="map"><rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}"/></clipPath>','<g clip-path="url(#map)">']
for name,d in land_paths(P,(LON0,LON1,LAT0,LAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
o.append('</g>')
draw_legs(o, P, L)
for la,lo in FJ:
    x,y=P(la,lo); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="mf-car ring" stroke-width="1.5"/>')
x,y=P(61.9,7.9); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink2 t-date halo">fjord road trip 13–19 Sep</text>')
cx,cy=P(*st['Copenhagen'][3:5]); o.append(f'<path class="m-flight" d="M{cx-330:.0f},{cy+40:.0f} Q{cx-160:.0f},{cy+70:.0f} {cx-8:.0f},{cy+2:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{cx-330:.0f}" y="{cy+58:.0f}" class="ink2 t-date halo">✈ from Seattle, 23–24 Aug</text>')
for s_ in S:
    if s_[1] in SIC:
        x,y=P(*s_[3:5]); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="dot ring" stroke-width="1.5"><title>{s_[0]}. {s_[1]}: {s_[2]}</title></circle>')
    else: draw_stop(o, P, s_)
# inset frame + pointer
bx0,by0=P(38.95,12.6); bx1,by1=P(36.8,16.3)
o.append(f'<rect x="{bx0:.0f}" y="{by0:.0f}" width="{bx1-bx0:.0f}" height="{by1-by0:.0f}" fill="none" class="frame" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>')
o.append(f'<line x1="{bx1:.0f}" y1="{(by0+by1)/2:.0f}" x2="{IX0:.0f}" y2="{IY0+IH/2:.0f}" class="frame" stroke-width="1" stroke-dasharray="4 3"/>')
o.append(f'<text x="{bx0:.0f}" y="{by0-6:.0f}" class="ink2 t-date halo">see inset →</text>')
pxx,pyy=P(*st['Palermo'][3:5]); o.append(f'<path class="m-flight" d="M{pxx-6:.0f},{pyy+2:.0f} Q{pxx-120:.0f},{pyy+70:.0f} {pxx-270:.0f},{pyy+40:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{pxx-272:.0f}" y="{pyy+62:.0f}" class="ink2 t-date halo">✈ home via Istanbul, 20 Nov</text>')
# inset
o.append(f'<rect x="{IX0-1}" y="{IY0-30}" width="{IW+2}" height="{IH+31:.0f}" rx="6" class="page" stroke-width="1.2" style="stroke:currentColor" opacity="1"/>')
o.append(f'<rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}" class="surface"/>')
o.append(f'<text x="{IX0+10}" y="{IY0-10}" class="ink t-stop">Calabria + Sicily, 9–20 Nov</text>')
o.append(f'<clipPath id="inset"><rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}"/></clipPath><g clip-path="url(#inset)">')
for name,d in land_paths(PI,(ILON0,ILON1,ILAT0,ILAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
SIC_L=[('train',[(38.75,15.92),'Reggio Calabria']),('train',['Reggio Calabria',(38.22,15.64)]),('ferry',[(38.22,15.64),(38.19,15.55)]),('train',[(38.19,15.55),'Catania']),('train',['Catania','Syracuse']),('train',['Catania','Taormina',(38.19,15.55),'Cefalù','Palermo'])]
draw_legs(o, PI, SIC_L)
ISTOP={'Reggio Calabria':(12,4,'start'),'Catania':(-12,4,'end'),'Syracuse':(-12,4,'end'),'Taormina':(-12,4,'end'),'Cefalù':(0,-14,'middle'),'Palermo':(-6,24,'start')}
for s_ in S:
    if s_[1] in SIC: dx,dy,anc=ISTOP[s_[1]]; draw_stop(o, PI, s_[:5]+(dx,dy,anc))
mx,my=PI(38.21,15.6); o.append(f'<text x="{mx-8:.0f}" y="{my-14:.0f}" class="ink2 t-date halo" text-anchor="end">Blu Jet ferry across the strait</text>')
xx,yy=PI(38.62,15.83); o.append(f'<text x="{xx:.0f}" y="{yy:.0f}" class="ink2 t-date halo" text-anchor="end">↑ train from Naples</text>')
o.append('</g>')
o.append(f'<text x="32" y="40" class="ink t-title">Europe 2026: Copenhagen → Palermo</text>')
o.append(f'<text x="32" y="64" class="ink2 t-sub">24 Aug – 20 Nov 2026 · 89 days in one Schengen stint · 29 stops · trains first · geographic layout (≈ = approximate dates)</text>')
ly=TOP+H_MAP+34; lx=32
o.append(f'<text x="{lx}" y="{ly-8}" class="ink t-stop">How each leg was travelled</text>')
for i,(k,v) in enumerate(MODES.items()):
    x0=lx+i*190; y0=ly+14; dash=f' stroke-dasharray="{v[2]}"' if v[2] else ''
    o.append(f'<line x1="{x0}" y1="{y0}" x2="{x0+44}" y2="{y0}" class="m-{k}" stroke-width="{v[3]+0.5}" stroke-linecap="round"{dash}/><text x="{x0+52}" y="{y0+4}" class="ink t-leg">{v[4]}</text>')
o.append(f'<text x="{lx}" y="{ly+52}" class="ink2 t-note">Bergen ⇄ Stockholm flown both ways. Tallinn ⇄ Helsinki by ferry. Ljubljana → Padua by bus to Trieste, then train. The Strait of Messina by Blu Jet ferry.</text>')
o.append(f'<text x="{lx}" y="{ly+72}" class="ink2 t-note">Full stop list with beds and guides: trips/europe-2026/README.md · Baltic rail detail: baltic-train-route.svg</text>')
o.append('</svg>')
open(OUT,'w').write('\n'.join(o)); print(OUT, W, H)
