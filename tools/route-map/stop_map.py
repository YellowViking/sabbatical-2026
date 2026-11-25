#!/usr/bin/env python3
"""Static stop maps for the trip guides: a Google Maps base (its own embed) + numbered, colour-coded pins.

Usage:
  python3 tools/route-map/stop_map.py maps.json OUTDIR
    maps.json = [{"id": "encarnacion", "w": 1200, "h": 620, "style": "World_Street_Map",
                  "points": [{"n": "1", "kind": "pick|bed|bus|sight|food|beer|hike|walk", "lat": .., "lng": ..}, ...]}, ...]
  → writes OUTDIR/<id>.html; screenshot each with tools/route-map/stop_map_shot.mjs (headless Chrome via pw.mjs) to <id>.jpg.

Base: Google Maps (`maps.google.com/maps?ll=…&z=…&output=embed`, "t": "m" roadmap or "p" terrain for hikes), with the pins drawn on top
at the same zoom. "base": "esri" falls back to Esri ArcGIS tiles ("style": "World_Street_Map" / "World_Topo_Map").
openstreetmap.org tiles return 403 to file:// pages, and CARTO now needs an API key, so don't switch back.
"""
import json, math, sys, os

COL = {'pick': '#2e7d32', 'bed': '#f9a825', 'bus': '#1565c0', 'sight': '#ef6c00', 'food': '#c62828',
       'beer': '#6a1b9a', 'hike': '#6d4c41', 'walk': '#00897b'}
TXT = {'bed': '#222'}


def px(lat, lng, z):
    s = 256 * 2 ** z
    x = (lng + 180) / 360 * s
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * s
    return x, y


def unpx(x, y, z):
    s = 256 * 2 ** z
    lng = x / s * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / s))))
    return lat, lng


def page(m):
    W, H, pad = m.get('w', 1200), m.get('h', 620), 70
    pts = m['points']
    z = 17
    while z > 3:
        xs, ys = zip(*[px(p['lat'], p['lng'], z) for p in pts])
        if max(xs) - min(xs) <= W - 2 * pad and max(ys) - min(ys) <= H - 2 * pad:
            break
        z -= 1
    z = min(z, m.get('maxz', 16))
    xs, ys = zip(*[px(p['lat'], p['lng'], z) for p in pts])
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    x0, y0 = cx - W / 2, cy - H / 2
    tiles = []
    if m.get('base', 'google') == 'google':
        # Google Maps' own embed, centred on the bbox centre at the same integer zoom (256-px Web Mercator, like the pins).
        # It is 2*T px taller than the frame and shifted up by T, which keeps the centre and hides the "View larger map" card;
        # Google's own logo and attribution are drawn again in the bottom corner.
        T = 70
        clat, clng = unpx(cx, cy, z)
        tiles.append(f'<iframe src="https://maps.google.com/maps?ll={clat:.6f},{clng:.6f}&z={z}&t={m.get("t", "m")}&hl=en&output=embed" '
                     f'style="position:absolute;left:0;top:-{T}px;width:{W}px;height:{H + 2 * T}px;border:0"></iframe>')
    else:
        for tx in range(int(x0 // 256), int((x0 + W) // 256) + 1):
            for ty in range(int(y0 // 256), int((y0 + H) // 256) + 1):
                n = 2 ** z
                tiles.append(f'<img src="https://server.arcgisonline.com/ArcGIS/rest/services/{m.get("style", "World_Street_Map")}/MapServer/tile/{z}/{ty}/{tx % n}" '
                             f'style="position:absolute;left:{tx * 256 - x0:.0f}px;top:{ty * 256 - y0:.0f}px;width:256px;height:256px">')
    pins = []
    for p in sorted(pts, key=lambda p: p['kind'] == 'pick'):
        x, y = px(p['lat'], p['lng'], z)
        c = COL.get(p['kind'], '#555')
        size = 34 if p['kind'] == 'pick' else 28
        label = '★' if p['kind'] == 'pick' and not p.get('n') else p.get('n', '')
        pins.append(f'<div style="position:absolute;left:{x - x0 - size / 2:.0f}px;top:{y - y0 - size / 2:.0f}px;width:{size}px;height:{size}px;'
                    f'border-radius:50%;background:{c};border:3px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.5);'
                    f'color:{TXT.get(p["kind"], "#fff")};font:bold {15 if size > 30 else 14}px/{size}px Helvetica,Arial,sans-serif;text-align:center">{label}</div>')
    legend = ''.join(f'<span style="display:inline-block;margin-right:12px"><span style="display:inline-block;width:12px;height:12px;border-radius:50%;'
                     f'background:{COL[k]};vertical-align:-1px;margin-right:4px"></span>{t}</span>'
                     for k, t in [('pick', 'bed pick'), ('bed', 'backup beds'), ('bus', 'arrival / bus'), ('sight', 'sights'), ('hike', 'hikes'),
                                  ('walk', 'walks'), ('food', 'food'), ('beer', 'drinks')] if any(p['kind'] == k for p in pts))
    return (f'<!doctype html><html><body style="margin:0"><div id="map" style="position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#e8e4da">'
            + ''.join(tiles) + ''.join(pins)
            + f'<div style="position:absolute;left:8px;bottom:8px;background:rgba(255,255,255,.88);padding:4px 8px;border-radius:4px;font:13px Helvetica,Arial,sans-serif;color:#222">{legend}</div>'
            + (f'<div style="position:absolute;right:6px;bottom:4px;font:11px Helvetica,Arial,sans-serif;color:#444;background:rgba(255,255,255,.75);padding:1px 4px">Map data © {__import__("datetime").date.today().year} Google</div>' if m.get('base', 'google') == 'google' else
               '<div style="position:absolute;right:6px;bottom:4px;font:11px Helvetica,Arial,sans-serif;color:#444;background:rgba(255,255,255,.7);padding:1px 4px">Tiles © Esri — Esri, HERE, Garmin, FAO, NOAA, USGS, © OpenStreetMap contributors</div>')
            + '</div></body></html>')


if __name__ == '__main__':
    maps, out = json.load(open(sys.argv[1])), sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for m in maps:
        open(os.path.join(out, m['id'] + '.html'), 'w').write(page(m))
        print(m['id'])
