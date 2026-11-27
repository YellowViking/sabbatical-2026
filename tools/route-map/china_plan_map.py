# China + Central Asia 2027 draft route map, same style as make_map.py. Usage:
#   curl -sLo /tmp/countries.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
#   python3 tools/route-map/china_plan_map.py /tmp/countries.geojson trips/china-2027/china-route-draft.svg
# Edit S (stops), L (legs by mode) to redraw. Days are trip days (Day 1 = arrival in Beijing).
import json, math, sys
GEO = sys.argv[1]; OUT = sys.argv[2]
LON0, LON1, LAT0, LAT1 = 57.5, 131.5, 28.8, 53.2
W = 1200; K = math.cos(math.radians(41)); SX = W / ((LON1 - LON0) * K); H_MAP = (LAT1 - LAT0) * SX
TOP = 96; PAD_B = 520; H = int(TOP + H_MAP + PAD_B)
def P(lat, lon): return ((lon - LON0) * K * SX, TOP + (LAT1 - lat) * SX)

# --- stops: (n, map label, list label, days, lat, lon, label dx, dy, anchor, optional?)
S = [
 (1,'Beijing 北京','Beijing 北京 + Great Wall hikes 长城','1–8',39.90,116.40, -12,4,'end',0),
 (2,'Mount Tai 泰山',"Tai'an 泰安: Mount Tai 泰山",'8–10',36.20,117.10, -12,4,'end',0),
 (3,'Qingdao 青岛','Qingdao 青岛','10–13',36.07,120.38, 12,4,'start',0),
 (4,'Shanghai 上海','Shanghai 上海','13–16',31.10,121.75, 12,6,'start',0),
 (5,'Suzhou 苏州','Suzhou 苏州','16–18',31.55,120.30, 4,-12,'end',0),
 (6,'Hangzhou 杭州','Hangzhou 杭州','18–21',30.27,120.15, 8,18,'start',0),
 (7,'Huangshan 黄山','Huangshan 黄山 + Hongcun 宏村','21–24',30.13,118.16, -12,8,'end',0),
 (8,'Pingyao 平遥','Pingyao 平遥','24–27',37.20,112.18, -12,4,'end',0),
 (9,"Xi'an 西安","Xi'an 西安 + Hua Shan 华山",'27–33',34.34,108.94, 0,22,'middle',0),
 (10,'Lanzhou 兰州','Lanzhou 兰州','33–34',36.06,103.83, 10,16,'start',0),
 (11,'Xining 西宁','Xining 西宁, Qinghai Lake 青海湖, Chaka 茶卡','34–38',36.62,101.78, -4,20,'end',0),
 (11.5,'Zigong 自贡 (family)','Zigong 自贡: family week over 五一 Labour Day','38–45',29.34,104.78, -12,5,'end',0),
 (12,'Zhangye 张掖','Zhangye 张掖: Rainbow Danxia 七彩丹霞','45–48',38.93,100.45, 12,4,'start',0),
 (13,'Jiayuguan 嘉峪关','Jiayuguan 嘉峪关','48–49',39.77,98.29, 8,-12,'start',0),
 (14,'Dunhuang 敦煌','Dunhuang 敦煌: Mingsha 鸣沙山, Mogao 莫高窟','49–53',40.14,94.66, 0,22,'middle',0),
 (15,'Turpan 吐鲁番','Turpan 吐鲁番','53–54',42.95,89.19, 10,16,'start',0),
 (16,'Urumqi 乌鲁木齐','Urumqi 乌鲁木齐 (twice; Tianchi 天山天池)','54–55 · 80–83',43.80,87.60, 12,-6,'start',0),
 (17,'Kashgar 喀什','Kashgar 喀什','55–60',39.47,75.99, 12,4,'start',0),
 (18,'Tashkurgan 塔什库尔干','Tashkurgan 塔什库尔干 + Karakul 喀拉库勒湖','60–64',37.77,75.23, 12,6,'start',0),
  (20,'Hulunbuir 呼伦贝尔','Hulunbuir 呼伦贝尔: Hailar, Enhe, Shiwei','64–71',49.21,119.74, -12,4,'end',0),
 (21,'Arxan 阿尔山','Arxan 阿尔山','71–74',47.17,119.94, -12,6,'end',0),
 (22,'Changbaishan 长白山','Harbin 哈尔滨 + Changbaishan 长白山 (opt.)','74–80',42.40,128.10, -12,18,'end',1),
 (23,'Kanas 喀纳斯 · Hemu 禾木','Kanas 喀纳斯, Hemu 禾木, Baihaba 白哈巴','83–92',48.70,87.02, 12,4,'start',0),
 (24,'Ili 伊犁','Ili 伊犁: Sayram, Nalati, Duku Hwy, Zhaosu','92–118',43.92,81.32, 2,-14,'middle',0),
 (25,'Almaty','🇰🇿 Almaty (QazETA needed)','118–122',43.24,76.95, -10,-10,'end',0),
 (26,'Kolsai · Charyn','Kolsai + Kaindy lakes, Charyn canyon','122–126',43.10,78.70, 12,-6,'start',0),
 (27,'Karakol','🇰🇬 Karakol: Ala-Kul trek','126–131',42.49,78.39, 12,10,'start',0),
 (28,'Issyk-Kul','Issyk-Kul south shore, Skazka canyon','131–133',42.12,76.99, 4,18,'middle',0),
 (29,'Song-Kol','Kochkor + Song-Kol yurts','133–137',41.85,75.13, -10,-8,'end',0),
 (30,'Naryn','Naryn + Tash Rabat','137–139',41.43,75.99, 12,8,'start',0),
 (31,'Bishkek','Bishkek + Ala-Archa','139–142',42.87,74.59, -10,-8,'end',0),
 (32,'Osh','Osh (start of the Pamir Highway)','142–144',40.40,72.45, -12,6,'end',0),
 (33,'Murghab','🇹🇯 Pamir Hwy to Murghab (GBAO permit)','144–147',38.17,73.96, 12,4,'start',0),
 (34,'Wakhan','Wakhan valley: Langar, Yamchun, Ishkashim','147–151',36.95,72.40, 10,16,'start',0),
 (35,'Khorog','Khorog','151–153',37.49,71.55, -12,4,'end',0),
 (36,'Dushanbe','Dushanbe (via Kalai-Khumb)','153–157',38.56,68.79, -4,20,'middle',0),
 (37,'Fann Mts','Fann Mts (Iskanderkul) + Penjikent','157–162',39.12,68.30, 12,-6,'start',0),
 (38,'Samarkand','🇺🇿 Samarkand','162–165',39.65,66.96, -6,-12,'end',0),
 (39,'Bukhara','Bukhara','165–168',39.77,64.42, 0,-14,'middle',0),
 (40,'Khiva','Khiva','168–170',41.38,60.36, 0,-14,'middle',0),
 (41,'Tashkent','Tashkent → ✈ home','170–172',41.30,69.24, 12,-4,'start',0),
]
st = {s[0]: s for s in S}
DISP = {s[0]: i for i, s in enumerate(S, 1)}   # display numbers (internal ids keep gaps)
# waypoints (not stops)
HARBIN, LIUYUAN, KASH = (45.75,126.65), (41.11,95.38), None
IRK, KHORGOS, KEGEN, KYZYLART, SARAZM = (39.70,73.92), (44.20,80.40), (42.95,79.10), (39.37,73.37), (39.50,67.45)
SARYTASH, KALAIKHUMB, PENJ, ALTAY, KUITUN = (39.73,73.25), (38.45,70.79), (39.50,67.61), (47.85,88.13), (44.43,84.90)
NALATI, ZHAOSU, SAYRAM = (43.30,84.00), (43.15,81.13), (44.60,81.20)
L = [
 ('train',[1,2,3,4,5,6,7]), ('train',[7,8,9,10,11]), ('flight',[11,11.5],0.22), ('flight',[11.5,10],-0.30), ('train',[10,11,12,13,14,LIUYUAN,15,16]), ('train',[16,17]),
 ('bus',[17,18,17]),
 ('flight',[17,20]), ('train',[20,21]),
 ('flight',[21,16]),
 ('train',[16,ALTAY]), ('bus',[ALTAY,23]), ('bus',[23,KUITUN]), ('train',[KUITUN,24]),
 ('bus',[24,KHORGOS,25]), ('bus',[25,26,KEGEN,27,28,29,30,31]), ('bus',[31,32]),
 ('jeep',[32,SARYTASH,KYZYLART,33,34,35,KALAIKHUMB,36]), ('bus',[36,37,PENJ,SARAZM,38]),
 ('train',[38,39,40]), ('train',[40,41]),
]
L_OPT = [('train',[21,HARBIN,22]), ('flight',[22,16])]
SPURS = [('bus',[24,SAYRAM]), ('bus',[24,NALATI]), ('bus',[24,ZHAOSU])]
MODES = {  # light, dark, dash, width, label  (slots 1–4 of the validated categorical palette, fixed order)
 'flight':('#2a78d6','#3987e5','2 6',2.5,'Flight'),
 'train': ('#7a5fd0','#9a83e6','',3,'Train (mostly high-speed)'),
 'bus':   ('#eb6834','#d95926','9 5',3,'Bus / shared taxi'),
 'jeep':  ('#eda100','#c98500','10 4 2 4',3,'4×4 (Pamir Highway)'),
}
def coords(i): return st[i][4:6] if isinstance(i,(int,float)) else i
def path(mode, items, proj, bend_k=0.14):
    ps=[proj(*coords(i)) for i in items]
    if mode=='flight':
        (x1,y1),(x2,y2)=ps; mx,my=(x1+x2)/2,(y1+y2)/2; dx,dy=x2-x1,y2-y1; nx,ny=-dy,dx; n=math.hypot(nx,ny) or 1
        bend=bend_k*math.hypot(dx,dy); sgn=-1 if ny>0 else 1; cx,cy=mx+nx/n*bend*sgn,my+ny/n*bend*sgn
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
  .surface { fill: #e6edf2; } .page { fill: #fcfcfb; } .land { fill: #fcfcfb; stroke: #d6d4cc; stroke-width: 0.8; } .china { fill: #f4f1e8; }
  .ink { fill: #0b0b0b; } .ink2 { fill: #52514e; } .ink3 { fill: #8a8984; } .halo { stroke: #fcfcfb; } .frame { stroke: #52514e; }
  .ring { stroke: #fcfcfb; } .dot { fill: #0b0b0b; } .num { fill: #fcfcfb; } .box { fill: #fcfcfb; stroke: #52514e; } .xing { fill: #fcfcfb; stroke: #0b0b0b; }
""" + ''.join(f"  .m-{k} {{ stroke: {v[0]}; }} .mf-{k} {{ fill: {v[0]}; }}\n" for k,v in MODES.items()) + """
  @media (prefers-color-scheme: dark) {
    .surface { fill: #0f1418; } .page { fill: #1a1a19; } .land { fill: #1a1a19; stroke: #383835; } .china { fill: #22211e; }
    .ink { fill: #f0efec; } .ink2 { fill: #c3c2b7; } .ink3 { fill: #8f8e86; } .halo { stroke: #1a1a19; } .frame { stroke: #c3c2b7; }
    .ring { stroke: #1a1a19; } .dot { fill: #f0efec; } .num { fill: #1a1a19; } .box { fill: #1a1a19; stroke: #c3c2b7; } .xing { fill: #1a1a19; stroke: #f0efec; }
""" + ''.join(f"    .m-{k} {{ stroke: {v[1]}; }} .mf-{k} {{ fill: {v[1]}; }}\n" for k,v in MODES.items()) + """  }
  .t-title { font-size: 22px; font-weight: 700; } .t-sub { font-size: 13px; }
  .t-stop { font-size: 12.5px; font-weight: 650; } .t-date { font-size: 10.5px; font-weight: 400; }
  .t-num { font-size: 9.5px; font-weight: 700; } .t-leg { font-size: 12.5px; } .t-note { font-size: 11.5px; }
  .t-country { font-size: 13px; font-weight: 600; letter-spacing: 2px; } .t-list { font-size: 11.5px; } .t-season { font-size: 11px; font-style: italic; }
  .halo { stroke-width: 3.5px; stroke-linejoin: round; paint-order: stroke; }
"""
def draw_legs(o, proj, legs, op=1.0):
    for leg in legs:
        mode,items=leg[0],leg[1]; bk=leg[2] if len(leg)>2 else 0.14
        c=MODES[mode]; dash=f' stroke-dasharray="{c[2]}"' if c[2] else ''; d=path(mode,items,proj,bk)
        o.append(f'<path class="ring" d="{d}" fill="none" stroke-width="{c[3]+3}" stroke-linecap="round" stroke-linejoin="round" opacity="{0.9*op:.2f}"/>')
        o.append(f'<path class="m-{mode}" d="{d}" fill="none" stroke-width="{c[3]}" stroke-linecap="round" stroke-linejoin="round" opacity="{op}"{dash}><title>{c[4]}</title></path>')
def draw_stop(o, proj, s, r=8.5):
    n,lab,full,days,la,lo,dx,dy,anc,opt=s; x,y=proj(la,lo)
    fade = ' opacity="0.5"' if opt else ''
    o.append(f'<g{fade}><title>{DISP[n]}. {full}: Day {days}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="dot ring" stroke-width="2"/>'
             f'<text x="{x:.1f}" y="{y+3.3:.1f}" class="num t-num" text-anchor="middle">{DISP[n]}</text>'
             f'<text x="{x+dx:.1f}" y="{y+dy:.1f}" class="ink t-stop halo" text-anchor="{anc}">{lab}</text></g>')

FONT = "system-ui, -apple-system, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif"
CA = set(range(25, 42))                 # stops outside China: small dots on the main map, full detail in the panel
PANEL_CN = {17, 18, 24}                          # Chinese stops repeated in the Central Asia panel
# Central Asia panel (below the main map)
ILON0, ILON1, ILAT0, ILAT1 = 59.6, 81.9, 36.3, 45.1
ISX = 44.0; IW = (ILON1 - ILON0) * K * ISX; IH = (ILAT1 - ILAT0) * ISX
IX0 = 20; IY0 = TOP + H_MAP + 64
def PI(lat, lon): return (IX0 + (lon - ILON0) * K * ISX, IY0 + (ILAT1 - lat) * ISX)
CAOFF = {17:(12,4,'start'),18:(12,4,'start'),19:(0,-13,'middle'),24:(-12,-9,'end'),25:(-12,-6,'end'),26:(10,-10,'start'),27:(12,6,'start'),
         28:(12,4,'start'),29:(-12,-6,'end'),30:(12,12,'start'),31:(-12,4,'end'),32:(-12,6,'end'),33:(12,4,'start'),34:(12,12,'start'),
         35:(-12,4,'end'),36:(0,22,'middle'),37:(10,-10,'start'),38:(0,-13,'middle'),39:(0,-13,'middle'),40:(0,-13,'middle'),41:(12,4,'start')}
LIST_Y = IY0 + IH + 44
H = int(LIST_Y + 20 + 14 * 17 + 16)
o=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="{FONT}">',
   '<title>China 中国 + Central Asia 2027 draft route: Beijing → Yangtze delta → Xi\'an → Silk Road → Xinjiang → far north → northern Xinjiang → Kazakhstan → Kyrgyzstan → Pamir → Uzbekistan</title>', f'<style>{CSS}</style>',
   f'<rect width="{W}" height="{H}" class="page"/>']
def base(proj, b, x0, y0, w, h, cid, labels):
    o.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" class="surface"/>')
    o.append(f'<clipPath id="{cid}"><rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}"/></clipPath><g clip-path="url(#{cid})">')
    for name,d in land_paths(proj, b):
        cls = 'land china' if name in ('China', 'Taiwan') else 'land'
        o.append(f'<path class="{cls}" d="{d}"><title>{name}</title></path>')
    for name,la,lo in labels:
        x,y=proj(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink3 t-country" text-anchor="middle">{name}</text>')
def season(proj, items):
    for txt,la,lo in items:
        x,y=proj(la,lo); o.append(f'<text x="{x:.0f}" y="{y:.0f}" class="ink2 t-season halo" text-anchor="middle">{txt}</text>')
def crossings(proj, small=False):
    for nm,(la,lo),lab,dx,dy,anc in [('Khorgos 霍尔果斯口岸',KHORGOS,'Khorgos 霍尔果斯',0,-10,'middle'),
                                  ('Kegen / Karkara',KEGEN,'Kegen',9,4,'start'),('Kyzyl-Art pass',KYZYLART,'Kyzyl-Art',-9,4,'end'),('Penjikent → Samarkand (Sarazm / Jartepa)',SARAZM,'',0,0,'start')]:
        x,y=proj(la,lo); r=3.5 if small else 4.5
        o.append(f'<g><title>Border crossing: {nm}</title><rect x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" transform="rotate(45 {x:.1f} {y:.1f})" class="xing" stroke-width="1.5"/>'
                 + (f'<text x="{x+dx:.0f}" y="{y+dy:.0f}" class="ink2 t-date halo" text-anchor="{anc}">{lab}</text>' if lab and not small else '') + '</g>')

# ---- main map
base(P,(LON0,LON1,LAT0,LAT1),0,TOP,W,H_MAP,'map',[('CHINA 中国',32.3,94.0),('MONGOLIA',46.6,103.0),('RUSSIA',52.2,95.0),('KAZAKHSTAN',48.2,68.0),('KOREA',36.3,127.9),('JAPAN',37.6,131.0),('INDIA',30.0,79.5),('PAKISTAN',30.2,68.5)])
season(P,[('Mar – Apr: north + Yangtze delta',41.6,111.0),('May: Silk Road 河西走廊 + southern Xinjiang 南疆',34.6,91.0),
          ('late May – Jun: grasslands of the far north',51.8,113.0),('Jun – Jul: northern Xinjiang 北疆, driest in summer',50.2,87.5)])
o.append('</g>')
fx0,fy0=P(ILAT1,ILON0); fx1,fy1=P(ILAT0,ILON1)
o.append(f'<rect x="{fx0:.0f}" y="{fy0:.0f}" width="{fx1-fx0:.0f}" height="{fy1-fy0:.0f}" fill="none" class="frame" stroke-width="1.2" stroke-dasharray="4 3" rx="4"/>')
o.append(f'<text x="{fx0+6:.0f}" y="{fy1-8:.0f}" class="ink2 t-date halo">Central Asia: see the panel below</text>')
draw_legs(o, P, L_OPT, op=0.45); draw_legs(o, P, SPURS, op=0.6); draw_legs(o, P, L)
crossings(P, small=True)
for s_ in S:
    if s_[0] in CA:
        x,y=P(*s_[4:6]); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"><title>{DISP[s_[0]]}. {s_[2]}: Day {s_[3]}</title></circle>')
    else: draw_stop(o, P, s_)
x,y=P(*HARBIN); o.append(f'<g opacity="0.5"><circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="dot ring" stroke-width="1.2"/><text x="{x+8:.0f}" y="{y+4:.0f}" class="ink2 t-date halo">Harbin 哈尔滨</text></g>')
bx,by=P(*coords(1)); sx,sy=P(33.2,131.2)
o.append(f'<path class="m-flight" d="M{sx:.0f},{sy:.0f} Q{bx+150:.0f},{by+120:.0f} {bx+7:.0f},{by+5:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{sx-4:.0f}" y="{sy-10:.0f}" class="ink2 t-date halo" text-anchor="end">✈ from Seattle via Manila, lands Day 1</text>')
# ---- Central Asia panel
o.append(f'<rect x="{IX0-1}" y="{IY0-32}" width="{IW+2:.0f}" height="{IH+33:.0f}" rx="6" class="box" stroke-width="1.2"/>')
o.append(f'<text x="{IX0+10}" y="{IY0-11}" class="ink t-stop">Central Asia, Day 118–172 (plus Kashgar and Tashkurgan in May)</text>')
base(PI,(ILON0,ILON1,ILAT0,ILAT1),IX0,IY0,IW,IH,'panel',[('KAZAKHSTAN',44.5,67.0),('UZBEKISTAN',41.9,64.6),('TURKMENISTAN',37.1,62.2),('KYRGYZSTAN',42.6,70.9),
      ('TAJIKISTAN',37.0,69.5),('AFGHANISTAN',36.5,65.0),('CHINA 中国',38.6,79.6)])
season(PI,[('Jul – Aug: Kazakhstan + the Kyrgyz highlands',44.75,72.6),('Aug: Pamir Highway, almost rainless',36.6,77.9),('Sep: Uzbekistan, after the heat',38.75,63.4),('May: Kashgar, Tashkurgan',38.2,78.8)])
o.append('</g>')
o.append('<g clip-path="url(#panel)">'); draw_legs(o, PI, SPURS, op=0.6); draw_legs(o, PI, L); crossings(PI); o.append('</g>')
for s_ in S:
    if s_[0] in CA or s_[0] in PANEL_CN:
        dx,dy,anc=CAOFF[s_[0]]; draw_stop(o, PI, s_[:6]+(dx,dy,anc,s_[9]), r=8)
x,y=PI(*coords(41)); o.append(f'<path class="m-flight" d="M{x+6:.0f},{y-6:.0f} Q{x+40:.0f},{y-90:.0f} {x+150:.0f},{y-130:.0f}" fill="none" stroke-width="2.5" stroke-dasharray="2 6" stroke-linecap="round"/>')
o.append(f'<text x="{x+152:.0f}" y="{y-136:.0f}" class="ink2 t-date halo" text-anchor="middle">✈ home to Seattle, Day 172</text>')
# ---- title
o.append(f'<text x="32" y="40" class="ink t-title">China 中国 + Central Asia 2027 (draft): follow the weather</text>')
o.append(f'<text x="32" y="64" class="ink2 t-sub">Day 1 = Tue 23 Mar 2027 (arrival in Beijing) · Day 38–45: family week in Zigong 自贡 · ✈ home from Tashkent ≈ Day 172 · ◆ = border crossing · faded = optional</text>')
# ---- legend (right of the panel)
lx=IX0+IW+40; ly=IY0-11
o.append(f'<text x="{lx}" y="{ly}" class="ink t-stop">How each leg is travelled</text>')
for i,(k,v) in enumerate(MODES.items()):
    y0=ly+24+i*24; dash=f' stroke-dasharray="{v[2]}"' if v[2] else ''
    o.append(f'<line x1="{lx}" y1="{y0}" x2="{lx+44}" y2="{y0}" class="m-{k}" stroke-width="{v[3]+0.5}" stroke-linecap="round"{dash}/><text x="{lx+52}" y="{y0+4}" class="ink t-leg">{v[4]}</text>')
y0=ly+24+4*24; o.append(f'<rect x="{lx+17}" y="{y0-5}" width="10" height="10" transform="rotate(45 {lx+22} {y0})" class="xing" stroke-width="1.5"/><text x="{lx+52}" y="{y0+4}" class="ink t-leg">Land border crossing</text>')
notes=['Flights: Seattle → Beijing, Xining → Chengdu (Zigong),','Yibin or Chengdu → Lanzhou, Kashgar → Hailar,','Arxan → Urumqi, Tashkent → Seattle. Everything','else by train, bus, shared taxi or 4×4.','',
       'China: one stay, Day 1 → 118, on the 10-year Q2 visa.','Kazakhstan: QazETA needed from 1 July 2027.','Pamir: GBAO permit ($20, fixed entry date).','Tashkurgan: border-area permit, in person,','at the police exit-entry office in Kashgar.','',
       'Weather: 10-year normals (Open-Meteo for China,','NASA POWER for Central Asia).','Route order and stop lengths only;','beds and legs come next.']
for i,t in enumerate(notes): o.append(f'<text x="{lx}" y="{ly+150+i*17}" class="ink2 t-note">{t}</text>')
# ---- stop list
o.append(f'<text x="32" y="{LIST_Y}" class="ink t-stop">Stops (trip days)</text>')
cols=[S[:14],S[14:28],S[28:]]
for ci,col in enumerate(cols):
    for ri,s_ in enumerate(col):
        x0=32+ci*390; y0=LIST_Y+20+ri*17; fade = ' opacity="0.55"' if s_[9] else ''
        o.append(f'<text x="{x0}" y="{y0}" class="ink t-list"{fade}><title>{s_[2]}</title><tspan font-weight="700">{DISP[s_[0]]}.</tspan> {s_[2]} <tspan class="ink2">Day {s_[3]}</tspan></text>')
o.append('</svg>')
open(OUT,'w').write('\n'.join(o)); print(OUT, W, H)
