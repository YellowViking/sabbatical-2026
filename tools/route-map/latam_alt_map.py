# LatAm alternatives map: the main route faded, the open options and add-ons from trips/latam/alternatives.md in colour.
# Reuses the base (projection, land, stops, legs) from latam_plan_map.py. Usage:
#   python3 tools/route-map/latam_alt_map.py /tmp/countries.geojson trips/latam/latam-alternatives-map.svg
import sys, os, math, json
SRC = open(os.path.join(os.path.dirname(__file__), 'latam_plan_map.py')).read()
exec(SRC[:SRC.index("o=[f'<svg")])          # defines W, H, P, S, L, CAL, MODES, land_paths, path, CSS, …

FLN, PDD, NAZ_, HUA, PAR = (-27.6,-48.5), (-34.04,-53.54), (-14.83,-74.94), (-14.09,-75.76), (-13.83,-76.25)
ALT = {  # key: (colour, dash, width, legend label)
 'B':  ('#c2185b', '9 5', 3.4, 'Plan B: Foz → Florianópolis (Christmas) → EGA/TTL bus to Montevideo, instead of Paraguay'),
 'B2': ('#7b1fa2', '2 5', 3.2, 'Plan B2: Florianópolis → Porto Alegre → Chuí → Punta del Diablo → Cabo Polonio'),
 'A2': ('#00838f', '9 5', 3.4, 'Plan A2: break the EGA ride from Encarnación in Salto (Uruguay)'),
 'C':  ('#2e7d32', '9 5', 3.4, 'Option C: Arequipa → Nazca → Huacachina → Paracas → Lima, award flight from Lima on 6 Feb'),
}
ALT_LEGS = [('B',['Foz do Iguaçu',FLN,POA,CHUY,'Montevideo']), ('B2',[CHUY,PDD,'Cabo Polonio']),
            ('A2',[CONC,SALTO_UY,'Montevideo']), ('C',['Arequipa',NAZ_,HUA,PAR,LIMA])]
# add-ons: (n, short label, legend text, lat, lon, dx, dy, anchor, inset)
ADD = [
 (1,'Nazca','⭐ Nazca Lines (with option C), +0–1 day',-14.83,-74.94,12,12,'start',False),
 (2,'Teresópolis','Teresópolis / Serra dos Órgãos, +2 before Rio',-22.41,-42.97,12,-8,'start',False),
 (3,'Cachi','Cachi + Calchaquí valleys, +2 (January storms)',-25.12,-66.16,-12,4,'end',False),
 (4,'Coroico','Coroico / Yungas after the Death Road, +1',-16.19,-67.72,12,-4,'start',False),
 (5,'Lunarejo','Valle del Lunarejo (Uruguay), +2 after New Year',-31.15,-55.95,12,4,'start',False),
 (6,'Ilha do Mel','Ilha do Mel after Curitiba, +1–2',-25.55,-48.31,12,6,'start',False),
 (7,'Santa Teresa','Santa Teresa park + Laguna Negra (B2 only), +0',-33.97,-53.55,12,-6,'start',False),
 (8,'Iberá','Esteros del Iberá (Plan A only), +2–3',-28.53,-57.17,-12,4,'end',False),
 (9,'Salto del Monday','Salto del Monday + Itaipú (Plan A only), +1',-25.57,-54.66,-12,-12,'end',False),
 (10,'Aparados','Aparados da Serra canyons (B2 only), +2',-29.17,-50.08,12,6,'start',False),
 (11,'San Blas','San Blas islands, +1',9.55,-78.95,0,16,'middle',True),
 (12,'Somoto','Somoto Canyon from Estelí, +1',13.48,-86.58,12,4,'start',True),
 (13,'trek','Monteverde → La Fortuna on foot, +1',10.4,-84.73,12,10,'start',True),
]
ALT_LINK = {'B':'florianopolis','B2':'florianopolis','A2':'encarnacion','C':'huacachina-paracas'}
ADDONS = 'alternatives.md#3-optional-add-ons-11-spare-days-before-15-mar'
ADD_LINK = {1:'huacachina-paracas', 2:'teresopolis', 12:'somoto'}
def addlink(n): return ADD_LINK.get(n, ADDONS)
def alt_path(o, proj, key, items):
    c,dash,w,_ = ALT[key]; d = path('bus', items, proj)
    o.append(f'<path class="ring" d="{d}" fill="none" stroke-width="{w+3}" stroke-linecap="round" stroke-linejoin="round" opacity="0.9" pointer-events="none"/>')
    o.append(alink(ALT_LINK[key], f'<path d="{d}" fill="none" stroke="{c}" stroke-width="{w}" stroke-dasharray="{dash}" stroke-linecap="round" stroke-linejoin="round"><title>{ALT[key][3]} (click for the guide)</title></path>'))
PANEL = [0, 0, 10**4, 10**4]   # x0, y0, x1, y1 of the current panel: nudged pins stay inside it
OBST = []   # (x, y, r) of everything clickable already placed in the current panel; pins are nudged off them
def add_pin(o, proj, a, r=8.5):
    n,lab,txt,la,lo,dx,dy,anc,_ = a; x0,y0 = proj(la,lo); x,y = x0,y0
    clear = lambda px,py: all(math.hypot(px-ox, py-oy) >= r + orad + 3 for ox,oy,orad in OBST) and PANEL[0]+r+2 <= px <= PANEL[2]-r-2 and PANEL[1]+r+2 <= py <= PANEL[3]-r-2
    if not clear(x,y):   # move the pin aside (up-right first) and draw a leader line to the real spot
        for dist in (19, 26, 34):
            for ang in (-45, -90, 0, -135, 45, 180, 90, 135):
                px,py = x0 + dist*math.cos(math.radians(ang)), y0 + dist*math.sin(math.radians(ang))
                if clear(px,py): x,y = px,py; break
            if (x,y) != (x0,y0): break
    lead = (f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x:.1f}" y2="{y:.1f}" stroke="#c98500" stroke-width="1.4" pointer-events="none"/>'
            f'<circle cx="{x0:.1f}" cy="{y0:.1f}" r="2.4" fill="#c98500" pointer-events="none"/>') if (x,y) != (x0,y0) else ''
    o.append(alink(addlink(n), f'<g><title>{n}. {txt}</title>{lead}<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#f9a825" class="ring" stroke-width="2"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" class="t-num" fill="#0b0b0b" text-anchor="middle">{n}</text>'
             + (f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="ink t-date halo" text-anchor="{anc}" pointer-events="none">{lab}</text>' if lab else '') + '</g>'))
    OBST.append((x, y, r))

HH = int(TOP + H_MAP + 320)
o=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {HH}" width="{W}" height="{HH}" font-family="system-ui, -apple-system, \'Segoe UI\', sans-serif">',
   '<title>Latin America v5: alternatives and add-ons</title>', f'<style>{CSS}</style>',
   f'<rect width="{W}" height="{HH}" class="page"/>', f'<rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}" class="surface"/>',
   f'<clipPath id="map"><rect x="0" y="{TOP}" width="{W}" height="{H_MAP:.0f}"/></clipPath>','<g clip-path="url(#map)">']
for name,d in land_paths(P,(LON0,LON1,LAT0,LAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
for name,la,lo in [('BRAZIL',-10,-52),('BOLIVIA',-17.5,-63.5),('PERU',-9,-75),('CHILE',-29,-71.6),('ARGENTINA',-30,-63),('PARAGUAY',-22.3,-58.5),('URUGUAY',-32.6,-55.9)]:
    x,y=P(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-country" text-anchor="middle">{name}</text>')
o.append('</g>')
draw_legs(o, P, L, op=0.22)                       # the main route, faded
PANEL[:] = [0, TOP, W, TOP + H_MAP]
for key,items in ALT_LEGS: alt_path(o, P, key, items)   # under the stops, so stops stay clickable
for s_ in S:
    if s_[1] in CA: continue
    x,y=P(*s_[3:5]); OBST.append((x, y, 6)); o.append(alink(GUIDES[s_[0]], f'<g opacity="0.55"><title>{s_[0]}. {s_[1]}: {s_[2]} (click for the guide)</title><circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="dot ring" stroke-width="1.5"/>'
                              f'<text x="{x:.1f}" y="{y+3:.1f}" class="num" font-size="7.5" font-weight="700" text-anchor="middle">{s_[0]}</text></g>'))
SLON0, SLON1, SLAT0, SLAT1 = -59.6, -47.6, -35.2, -24.9          # the south-east corner, zoomed in an inset
inSE = lambda la,lo: SLAT0 <= la <= SLAT1 and SLON0 <= lo <= SLON1
PTS = [('Florianópolis',FLN,-10,4,'end'),('Porto Alegre',POA,12,4,'start'),('Chuí',CHUY,-10,-4,'end'),('Punta del Diablo',PDD,12,14,'start'),
       ('Salto (A2)',SALTO_UY,4,17,'start'),('Huacachina',HUA,-10,10,'end'),('Paracas',PAR,-10,-2,'end'),('Lima',LIMA,-10,4,'end')]
for nm,(la,lo),dx,dy,anc in PTS:
    x,y=P(la,lo); OBST.append((x, y, 3.5)); lab='' if inSE(la,lo) else f'<text x="{x+dx:.0f}" y="{y+dy:.0f}" class="ink t-date halo" text-anchor="{anc}">{nm}</text>'
    o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" class="dot ring" stroke-width="1.2"/>{lab}')
for a in ADD:
    if a[8]: continue
    if inSE(a[3],a[4]): add_pin(o, P, a[:1]+('',)+a[2:], r=7)
    else: add_pin(o, P, a)
# zoom frame on the main map, pointing to the inset
zx0,zy0=P(SLAT1,SLON0); zx1,zy1=P(SLAT0,SLON1)
o.append(f'<rect x="{zx0:.0f}" y="{zy0:.0f}" width="{zx1-zx0:.0f}" height="{zy1-zy0:.0f}" fill="none" class="frame" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>')
SW_ = 262; SK = math.cos(math.radians(30)); SSX = SW_/((SLON1-SLON0)*SK); SH_ = (SLAT1-SLAT0)*SSX
SX0 = 14; SY0 = TOP + H_MAP - SH_ - 6
def PSE(lat, lon): return (SX0 + (lon-SLON0)*SK*SSX, SY0 + (SLAT1-lat)*SSX)
o.append(f'<line x1="{zx0:.0f}" y1="{(zy0+zy1)/2:.0f}" x2="{SX0+SW_+1:.0f}" y2="{SY0+SH_/2:.0f}" class="frame" stroke-width="1" stroke-dasharray="4 3"/>')
o.append(f'<rect x="{SX0-1}" y="{SY0-30:.0f}" width="{SW_+2}" height="{SH_+31:.0f}" rx="6" class="box" stroke-width="1.2"/>')
o.append(f'<rect x="{SX0}" y="{SY0:.0f}" width="{SW_}" height="{SH_:.0f}" class="surface"/>')
o.append(alink('alternatives.md#1-christmas-week-paraguay-plan-a-or-florianópolis-plan-b--decide-by--15-dec', f'<text x="{SX0+10}" y="{SY0-10:.0f}" class="ink t-stop">Christmas week: Paraguay or the coast</text>'))
o.append(f'<clipPath id="se"><rect x="{SX0}" y="{SY0:.0f}" width="{SW_}" height="{SH_:.0f}"/></clipPath><g clip-path="url(#se)">')
for name,d in land_paths(PSE,(SLON0,SLON1,SLAT0,SLAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
draw_legs(o, PSE, L, op=0.3); OBST.clear(); PANEL[:] = [SX0, SY0, SX0+SW_, SY0+SH_]
for key,items in ALT_LEGS: alt_path(o, PSE, key, items)
for s_ in S:
    if s_[1] in CA or not inSE(*s_[3:5]): continue
    x,y=PSE(*s_[3:5]); OBST.append((x, y, 6)); o.append(alink(GUIDES[s_[0]], f'<g opacity="0.6"><title>{s_[0]}. {s_[1]}: {s_[2]} (click for the guide)</title><circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="dot ring" stroke-width="1.5"/>'
                                f'<text x="{x:.1f}" y="{y+3:.1f}" class="num" font-size="7.5" font-weight="700" text-anchor="middle">{s_[0]}</text></g>'))
for nm,(la,lo),dx,dy,anc in PTS:
    if inSE(la,lo):
        x,y=PSE(la,lo); OBST.append((x, y, 3.5)); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" class="dot ring" stroke-width="1.2"/><text x="{x+dx:.0f}" y="{y+dy:.0f}" class="ink t-date halo" text-anchor="{anc}">{nm}</text>')
SE_LAB = {5:(12,4,'start'),6:(-12,-6,'end'),7:(12,-6,'start'),8:(12,4,'start'),9:(-12,4,'end'),10:(-12,-8,'end')}
for a in ADD:
    if not a[8] and inSE(a[3],a[4]):
        dx,dy,anc=SE_LAB.get(a[0],(12,4,'start')); add_pin(o, PSE, a[:5]+(dx,dy,anc)+a[8:], r=7.5)
o.append('</g>')
# Central America inset (top right), main route faded, add-ons in colour
bx0,by0=P(13.9,-88.6); bx1,by1=P(7.7,-79.0)
o.append(f'<rect x="{bx0:.0f}" y="{by0:.0f}" width="{bx1-bx0:.0f}" height="{by1-by0:.0f}" fill="none" class="frame" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>')
ILON0, ILON1, ILAT0, ILAT1 = -88.6, -78.4, 7.7, 13.9
IH_T = 262; IK = math.cos(math.radians(11)); ISX = IH_T/(ILAT1-ILAT0); IH = IH_T; IW = int((ILON1-ILON0)*IK*ISX)
IX0 = W - IW - 14; IY0 = TOP + 40
def PI(lat, lon): return (IX0 + (lon-ILON0)*IK*ISX, IY0 + (ILAT1-lat)*ISX)
o.append(f'<line x1="{bx1:.0f}" y1="{(by0+by1)/2:.0f}" x2="{IX0-1:.0f}" y2="{IY0+IH/2:.0f}" class="frame" stroke-width="1" stroke-dasharray="4 3"/>')
o.append(f'<rect x="{IX0-1}" y="{IY0-30}" width="{IW+2}" height="{IH+31:.0f}" rx="6" class="box" stroke-width="1.2"/>')
o.append(f'<rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}" class="surface"/>')
o.append(f'<text x="{IX0+10}" y="{IY0-10}" class="ink t-stop">Central America add-ons</text>')
o.append(f'<clipPath id="inset"><rect x="{IX0}" y="{IY0}" width="{IW}" height="{IH:.0f}"/></clipPath><g clip-path="url(#inset)">')
for name,d in land_paths(PI,(ILON0,ILON1,ILAT0,ILAT1)): o.append(f'<path class="land" d="{d}"><title>{name}</title></path>')
draw_legs(o, PI, CAL, op=0.22)
OBST.clear(); PANEL[:] = [IX0, IY0, IX0+IW, IY0+IH]
for s_ in S:
    if s_[1] in CA and s_[0] not in OPTIONAL:
        x,y=PI(*s_[3:5]); OBST.append((x, y, 4))
        o.append(alink(GUIDES[s_[0]], f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="dot ring" stroke-width="1" opacity="0.6"><title>{s_[0]}. {s_[1]}: {s_[2]} (click for the guide)</title></circle>'))
x1,y1=PI(*st['Monteverde'][3:5]); x2,y2=PI(*st['La Fortuna / Arenal'][3:5])
o.append(f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" fill="none" stroke="#6d4c41" stroke-width="3.2" stroke-dasharray="2 5" stroke-linecap="round" pointer-events="none"><title>Monteverde → La Fortuna on foot</title></path>')
for a in ADD:
    if a[8]: add_pin(o, PI, a, r=7.5)
o.append('</g>')
# title
o.append(f'<text x="32" y="40" class="ink t-title">Latin America v5: alternatives and add-ons (decide on the road)</text>')
o.append(f'<text x="32" y="64" class="ink2 t-sub">Faded = main route · coloured lines = open options · yellow pins = add-ons for the spare days · click a stop, line or pin for its guide</text>')
# legend
ly=TOP+H_MAP+30; lx=32
o.append(f'<text x="{lx}" y="{ly}" class="ink t-stop">Open options</text>')
for i,(k,v) in enumerate(ALT.items()):
    y0=ly+22+i*20
    o.append(alink(ALT_LINK[k], f'<line x1="{lx}" y1="{y0}" x2="{lx+44}" y2="{y0}" stroke="{v[0]}" stroke-width="{v[2]}" stroke-dasharray="{v[1]}" stroke-linecap="round"/><text x="{lx+54}" y="{y0+4}" class="ink t-leg">{v[3]}</text>'))
ty=ly+22+len(ALT)*20+18
o.append(f'<text x="{lx}" y="{ty}" class="ink t-stop">Add-ons (yellow pins; ⭐ = my pick)</text>')
for i,a in enumerate(ADD):
    col,row=divmod(i,7); x0=lx+col*480; y0=ty+20+row*17
    o.append(alink(addlink(a[0]), f'<text x="{x0}" y="{y0}" class="ink t-list"><tspan font-weight="700">{a[0]}.</tspan> {a[2]}</text>'))
o.append(f'<text x="{lx}" y="{ty+20+7*17+12}" class="ink2 t-note">Added to the main route on 26 Nov: a 2nd Potosí night (it took the Copacabana-town night). Decided: keep the route order; no northern Brazil entry.</text>')
o.append('</svg>')
OUT=sys.argv[2]; open(OUT,'w').write('\n'.join(o)); print(OUT, W, HH)
