import fs from 'node:fs/promises';

const STOPS = [
  ['copenhagen', 'Nyhavn'],
  ['gothenburg', 'Gothenburg'],
  ['oslo', 'Oslo Opera House'],
  ['stavanger', 'Preikestolen'],
  ['bergen', 'Nærøyfjord'],
  ['stockholm', 'Gamla stan'],
  ['gotland', 'Visby'],
  ['helsinki', 'Suomenlinna'],
  ['tallinn', 'Tallinn'],
  ['riga', 'Riga'],
  ['vilnius', 'Vilnius'],
  ['slovenia', 'Lake Bled'],
  ['croatia', 'Dubrovnik'],
  ['italy', 'Amalfi Coast'],
];

const UA = { 'User-Agent': 'sabbatical-itinerary-site/1.0 (https://github.com/YellowViking/sabbatical-2026; personal use)' };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const strip = (s) => (s || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();

// https://upload.wikimedia.org/wikipedia/commons/a/ab/Foo.jpg
//   -> https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Foo.jpg/1400px-Foo.jpg
function thumbUrl(rawSrc, width = 1280) {
  const src = rawSrc.split('?')[0];
  const m = src.match(
    /^(https:\/\/upload\.wikimedia\.org\/wikipedia\/(?:commons|en))\/(?:thumb\/)?([0-9a-f])\/([0-9a-f]{2})\/([^/]+)/
  );
  if (!m) return src;
  const [, base, d1, d2, name] = m;
  const rendered = /\.svg$/i.test(name) ? `${name}.png` : name;
  return `${base}/thumb/${d1}/${d2}/${name}/${width}px-${rendered}`;
}

const out = {};

for (const [slug, title] of STOPS) {
  try {
    const sum = await fetch(
      `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`,
      { headers: UA }
    ).then((r) => r.json());
    await sleep(700);

    const src = sum.originalimage?.source || sum.thumbnail?.source;
    if (!src) { console.log(`${slug}: NO IMAGE (${title})`); continue; }
    const file = decodeURIComponent(src.split('?')[0].split('/').pop().replace(/^\d+px-/, ''));

    // Wikimedia only serves a fixed set of thumbnail widths; 1280 then 500.
    let res, url;
    for (const w of [1280, 500]) {
      url = thumbUrl(src, w);
      res = await fetch(url, { headers: UA });
      await sleep(500);
      if (res.ok) break;
    }
    if (!res.ok) { console.log(`${slug}: img HTTP ${res.status}  ${url}`); continue; }
    const buf = Buffer.from(await res.arrayBuffer());
    const ext = (res.headers.get('content-type') || '').includes('png') ? 'png' : 'jpg';
    await fs.writeFile(`images/${slug}.${ext}`, buf);
    await sleep(700);

    let artist = '', license = '';
    try {
      const q = new URL('https://commons.wikimedia.org/w/api.php');
      q.searchParams.set('action', 'query');
      q.searchParams.set('titles', `File:${file}`);
      q.searchParams.set('prop', 'imageinfo');
      q.searchParams.set('iiprop', 'extmetadata');
      q.searchParams.set('format', 'json');
      const info = await fetch(q, { headers: UA }).then((r) => r.json());
      const page = Object.values(info.query.pages)[0];
      const m = page?.imageinfo?.[0]?.extmetadata || {};
      artist = strip(m.Artist?.value);
      license = strip(m.LicenseShortName?.value);
    } catch {}
    await sleep(700);

    out[slug] = { src: `images/${slug}.${ext}`, file, title, artist, license };
    console.log(`${slug}: ${Math.round(buf.length / 1024)}KB  — ${artist} / ${license}`);
  } catch (e) {
    console.log(`${slug}: FAILED ${e.message}`);
    await sleep(1000);
  }
}

await fs.writeFile('images/credits.json', JSON.stringify(out, null, 2));
console.log(`\ndone: ${Object.keys(out).length}/${STOPS.length}`);
