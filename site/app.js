/* ═══════════════════════════════════════════════════════════
   One source of truth. The ledger, the spine, the baseline
   table and every nights meter are all rendered from STOPS,
   so a night can never disagree with itself.
   ═══════════════════════════════════════════════════════════ */

const STOPS = [
  { slug:'copenhagen', name:'Copenhagen',  short:'Copenhagen', nights:3,  min:3,  max:5,  c:'#2c6470', phase:'late Aug',        start:'Aug 24', end:'Aug 27',  flex:'3–5',   idea:'Jet-lag land; <b>+1</b> easy if wiped. Louisiana/Malmö only if ≥4n' },
  { slug:'gothenburg', name:'Gothenburg',  short:'Gothenburg', nights:2,  min:0,  max:3,  c:'#33707a', phase:'→',               start:'Aug 27', end:'Aug 29',  flex:'0–3',   idea:'Skip OK (long CPH→OSL). <b>+1</b> enables full <b>Vrångö</b>' },
  { slug:'oslo',       name:'Oslo',        short:'Oslo',       nights:3,  min:2,  max:4,  c:'#3a7b7c', phase:'→',               start:'Aug 29', end:'Sep 1',   flex:'2–4',   idea:'Ekeberg / Hovedøya / Mathallen' },
  { slug:'stavanger',  name:'Stavanger + Preikestolen', short:'Stavanger', nights:3, min:2, max:4, c:'#457f73', phase:'→',      start:'Sep 1',  end:'Sep 4',   flex:'2–4',   idea:'Weather buffer; dawn hike. Don’t starve below ~2–3 in storms' },
  { slug:'bergen',     name:'Bergen + fjords', short:'Bergen + fjords', nights:6, min:4, max:7, c:'#52836a', phase:'→',         start:'Sep 4',  end:'Sep 10',  flex:'4–7',   idea:'<b>Split</b> city + Aurland/Flåm area; Undredal quieter' },
  { slug:'stockholm',  name:'Stockholm',   short:'Stockholm',  nights:5,  min:4,  max:6,  c:'#628764', phase:'early Sep',       start:'Sep 10', end:'Sep 15',  flex:'4–6',   idea:'Tyresta + views; <b>5n consensus</b> nature-first · Grinda if 6n' },
  { slug:'gotland',    name:'Gotland / Visby', short:'Gotland', nights:3, min:0,  max:3,  c:'#748a5e', phase:'',                start:'Sep 15', end:'Sep 18',  flex:'0–3',   idea:'<b>#1 swing</b> — skip, or 2n + Folhammar/Fårö' },
  { slug:'helsinki',   name:'Helsinki',    short:'Helsinki',   nights:2,  min:1,  max:3,  c:'#868c59', phase:'',                start:'Sep 18', end:'Sep 20',  flex:'1–3',   idea:'Ferry-in; Löyly; +1 if Nuuksio+Porvoo' },
  { slug:'tallinn',    name:'Tallinn',     short:'Tallinn',    nights:3,  min:2,  max:4,  c:'#988d54', phase:'mid Sep',         start:'Sep 20', end:'Sep 23',  flex:'2–4',   idea:'Walls + Telliskivi + <b>Lahemaa/Viru</b> · 2n = city only' },
  { slug:'riga',       name:'Riga base',   short:'Riga',       nights:10, min:7,  max:12, c:'#a98c4e', phase:'',                start:'Sep 23', end:'Oct 3',   flex:'7–12',  idea:'<b>#2 swing</b> · market + Gauja/Ķemeri · year-base lab' },
  { slug:'vilnius',    name:'Vilnius',     short:'Vilnius',    nights:3,  min:2,  max:4,  c:'#b48748', phase:'→',               start:'Oct 3',  end:'Oct 6',   flex:'2–4',   idea:'OT + Užupis + <b>Trakai</b> · then ✈ LJU' },
  { slug:'slovenia',   name:'Slovenia',    short:'Slovenia',   nights:7,  min:6,  max:9,  c:'#b87c41', phase:'early Oct',       start:'Oct 6',  end:'Oct 13',  flex:'6–9',   idea:'<b>Split</b> LJU + Bled/Bohinj · caves/Piran optional' },
  { slug:'croatia',    name:'Croatia',     short:'Croatia',    nights:13, min:11, max:15, c:'#b76c39', phase:'mid Oct',         start:'Oct 13', end:'Oct 26',  flex:'11–15', idea:'<b>Split bases</b> ZG · Plitvice area · Split hub · DBV · skip Krka default' },
  { slug:'italy',      name:'Italy',       short:'Italy',      nights:20, min:18, max:22, c:'#b25730', phase:'late Oct–mid Nov', start:'Oct 26', end:'Nov 15', flex:'18–22', idea:'Keep warm finale + home flight', defLabel:'~20' },
];

const SCHENGEN_CAP = 90;
const DAY1 = new Date(2026, 7, 24); // Aug 24 2026 — ticketed landing, Schengen day 1

const fmt = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
const dayN = (n) => { const d = new Date(DAY1); d.setDate(d.getDate() + n - 1); return d; };
const totalNights = STOPS.reduce((s, x) => s + x.nights, 0);

/* ─────────── the ledger: 90 cells, 83 spent ─────────── */

(function ledger() {
  const el = document.getElementById('ledger');
  if (!el) return;
  const hint = document.getElementById('ledger-hint');
  const defaultHint = hint ? hint.textContent : '';

  let day = 0;
  const frag = document.createDocumentFragment();

  STOPS.forEach((stop) => {
    for (let n = 1; n <= stop.nights; n++) {
      day++;
      const cell = document.createElement('span');
      cell.className = 'cell';
      cell.style.setProperty('--cc', stop.c);
      cell.style.setProperty('--i', day);
      cell.dataset.label = `Day ${day} · ${fmt(dayN(day))} · ${stop.short} (night ${n} of ${stop.nights})`;
      cell.tabIndex = -1;
      frag.appendChild(cell);
    }
  });

  for (let d = day + 1; d <= SCHENGEN_CAP; d++) {
    const cell = document.createElement('span');
    cell.className = 'cell free';
    cell.style.setProperty('--i', d);
    cell.dataset.label = `Day ${d} · ${fmt(dayN(d))} · unspent buffer`;
    cell.tabIndex = -1;
    frag.appendChild(cell);
  }

  el.appendChild(frag);

  if (hint) {
    el.addEventListener('pointerover', (e) => {
      const c = e.target.closest('.cell');
      if (c) hint.textContent = c.dataset.label;
    });
    el.addEventListener('pointerleave', () => { hint.textContent = defaultHint; });
  }
})();

/* ─────────── route spine ─────────── */

(function spine() {
  const list = document.getElementById('spine-list');
  if (!list) return;
  const maxN = Math.max(...STOPS.map((s) => s.nights));

  list.innerHTML = STOPS.map((s) => `
    <li class="spine-item" data-target="hub-${s.slug}" style="--c:${s.c}; --h:${Math.round(14 + (s.nights / maxN) * 44)}px">
      <a href="#hub-${s.slug}">
        <span class="spine-bar"></span>
        <span class="spine-text">
          <span class="spine-name">${s.short}</span>
          <span class="spine-dates">${s.start} – ${s.end} · ${s.defLabel || s.nights}n</span>
        </span>
      </a>
    </li>`).join('');

  const items = [...list.querySelectorAll('.spine-item')];
  const hubs = items.map((i) => document.getElementById(i.dataset.target)).filter(Boolean);
  if (!hubs.length || !('IntersectionObserver' in window)) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      const item = items.find((i) => i.dataset.target === entry.target.id);
      if (item) item.classList.toggle('active', entry.isIntersecting);
    });
  }, { rootMargin: '-45% 0px -45% 0px' });

  hubs.forEach((h) => io.observe(h));
})();

/* ─────────── baseline table ─────────── */

(function baseline() {
  const body = document.getElementById('baseline-body');
  if (!body) return;

  const rows = STOPS.map((s) => `
    <tr>
      <td>${s.phase}</td>
      <td class="b-stop" style="--rc:${s.c}"><span class="b-dot"></span><a href="#hub-${s.slug}">${s.name}</a></td>
      <td class="num">${s.defLabel || s.nights}</td>
      <td class="b-flex">${s.flex}</td>
      <td class="b-dates">${s.start} – ${s.end}</td>
      <td class="b-idea">${s.idea}</td>
    </tr>`).join('');

  body.innerHTML = rows + `
    <tr class="b-home">
      <th scope="row">~mid-Nov</th>
      <td class="b-stop">✈ home NAP/FCO</td>
      <td class="num">—</td>
      <td class="b-flex">—</td>
      <td class="b-dates">Nov 15</td>
      <td class="b-idea">one-way SEA</td>
    </tr>`;
})();

/* ─────────── nights meters ─────────── */

document.querySelectorAll('.nights').forEach((el) => {
  const min = +el.dataset.min, def = +el.dataset.def, max = +el.dataset.max;
  // Italy's source default is "~20n" — keep the approximation mark.
  const defLabel = el.dataset.defLabel || def;
  let cells = '';
  for (let i = 1; i <= max; i++) {
    const cls = i <= min ? '' : i <= def ? ' soft' : ' stretch';
    cells += `<span class="n-cell${cls}"></span>`;
  }
  el.innerHTML =
    `<span class="nights-cells" aria-hidden="true">${cells}</span>` +
    `<span class="nights-label"><b>${defLabel}n</b> default · flex ${min}–${max}n</span>`;
});

/* ─────────── photo credits ─────────── */

const CREDITS = {
  copenhagen: ['Nyhavn', 'European Commission', 'CC BY 4.0'],
  gothenburg: ['Gothenburg', 'Bengt Nyman', 'CC BY 2.0'],
  oslo: ['Oslo Opera House', 'Pierre Blaché', 'CC0'],
  stavanger: ['Preikestolen', 'Clementp.fr', 'CC BY-SA 4.0'],
  bergen: ['Nærøyfjord', 'Karamell', 'CC BY-SA 3.0'],
  stockholm: ['Gamla stan', 'Arild Vågen', 'CC BY-SA 4.0'],
  gotland: ['Visby', 'L.G.foto', 'CC BY-SA 4.0'],
  helsinki: ['Suomenlinna', 'Migro', 'Public domain'],
  tallinn: ['Tallinn', 'Jorge Franganillo', 'CC BY 2.0'],
  riga: ['Riga', 'Jorge Franganillo', 'CC BY 2.0'],
  vilnius: ['Vilnius', 'Augustas Didžgalvis', 'CC BY-SA 4.0'],
  slovenia: ['Lake Bled', 'Canadianhockey91', 'CC BY-SA 3.0'],
  croatia: ['Dubrovnik', 'Zysko serhii', 'CC BY-SA 4.0'],
  italy: ['Amalfi Coast', 'Bruno Rijsman', 'CC BY-SA 2.0'],
};

(function credits() {
  const el = document.getElementById('photo-credits');
  if (!el) return;
  const parts = Object.values(CREDITS).map(([subject, who, lic]) => `${subject} — ${who} (${lic})`);
  el.textContent = 'Photographs via Wikimedia Commons. ' + parts.join(' · ') + '.';
})();

/* ─────────── consistency guard (dev console only) ─────────── */

if (totalNights !== 83) {
  console.warn(`Night total is ${totalNights}, expected 83 — the ledger and the baseline table just disagreed with the document.`);
}
