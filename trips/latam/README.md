# Latin America: next leg (planning)

**Status:** planning. Window: **December → mid-March**. No route or dates are fixed yet.

This page will become the trip's single source of truth, like [Europe 2026](../europe-2026/README.md): a route table, links to one guide per place in `guides/`, how the trip was planned, and the lessons.

## Already visited (skip these)

From [blog.buyuchen.org](https://blog.buyuchen.org) plus trips the blog doesn't cover:

| Country | When | Places |
|---|---|---|
| Colombia | Nov 2023 – Jan 2024 | Cartagena, Santa Marta, Minca, Tayrona, Lost City trek, Medellín (Guatapé), Salento/Cocora, Cali, Popayán, Pasto/Ipiales, Bogotá |
| Ecuador | Jan – Apr 2024 | Ibarra, Quito (Pichincha), Galápagos, Guayaquil, Cuenca, Baños, Latacunga/Quilotoa, the Amazon |
| Peru | Dec 2019 · Apr – May 2024 | Cusco, Machu Picchu (2019) · Chiclayo, Chan Chan (Trujillo), Huaraz, Lima (2024) |
| El Salvador | May 2024 | San Salvador, Santa Ana, Ruta de las Flores, the 7 waterfalls |
| Guatemala | twice, latest 2024 | Guatemala City, Antigua, Tikal |
| Mexico | 2016 · 2022 · Mar – Apr 2025 | Cancún area (2016; a week of remote work there in 2022) · Querétaro, San Miguel de Allende, Guanajuato, Oaxaca, Puebla, Mexico City (2025) |
| Belize | 2016 | |
| Argentina | earlier trips · Dec 2025 – Jan 2026 | Ushuaia / Tierra del Fuego (visited extensively) · Buenos Aires, Mendoza, Bariloche, El Calafate, El Chaltén |
| Transit only | | Panama (airport stopover), Honduras (connection) |

**Lessons from Argentina, Dec 2025 – Jan 2026:**
- Peak season (Dec–Jan) made it the most expensive trip so far, mostly in flights.
- Fly straight to El Calafate rather than detouring, and do Chile over land.
- Refugio reservations are the bottleneck.
- Mendoza deserved more time, for the mountains to the north.

## Not yet visited, with December – mid-March conditions

| Region | Conditions |
|---|---|
| **Chile** top to bottom: Atacama, Santiago/Valparaíso, the lakes and Chiloé, the Carretera Austral, Torres del Paine, Punta Arenas | Summer. Chile's own holiday peak is Jan–Feb; late Feb–March is shoulder season |
| **Southern Mexico:** Chiapas (San Cristóbal, Palenque, Sumidero Canyon); the Tren Maya beyond Cancún (Mérida, Campeche, Bacalar) | Dry season |
| **Honduras** (Copán, Utila), **Nicaragua** (León, Ometepe), **Costa Rica**, **Panama** (Boquete, San Blas) | Dry season. Costa Rica's cloud forest stays changeable |
| Bolivia, Brazil, Uruguay, Paraguay | Rainy or hot and humid; Carnival is about 5–10 Feb 2027 |
| Argentina's north-west (Salta, Jujuy) | Summer rains: better in another season |

## Draft route v3 (21 Nov 2026): consensus days, 2-week floating buffer

**How it was chosen:**
- [`tools/route-optimizer/opt.py`](../../tools/route-optimizer/opt.py) tries every order of the regions and every start day from 1 to 20 Dec.
- It scores **expected wet days**, using each region's wet-day share per month from Open-Meteo 10-year normals, plus **2 wet-day equivalents per 1,000 km flown**. It adds a travel day per long hop.
- **Days per region are the typical backpacker stay** (blogs, Reddit, Wikivoyage, Hostelworld, Nomadic Matt, The Broke Backpacker; researched 21 Nov 2026). Nothing is padded to fill the window.
- **A 2-week buffer floats.** The plan must end 14 days before 15 Mar, so the buffer can go wherever the trip needs it. Any other slack means a later start or an earlier return.

**Typical days per region (short / typical / full):**

| Region | Short | Typical | Full | Notes |
|---|---|---|---|---|
| Brazil: Fortaleza → Jericoacoara | 3 | 4 | 5 | Lençóis Maranhenses +3 optional: its lagoons are mostly dry in December |
| Brazil: Pipa + Olinda | 3 | 4 | 5 | "11 days was excessive" |
| Brazil: Salvador + Chapada Diamantina | 6 | 8 | 10 | Chapada ≥ 4 nights; the Vale do Pati trek is 4–5 days |
| Brazil: Rio + Paraty/Ilha Grande + Iguaçu | 8 | 9 | 13 | Rio 4, Paraty/Ilha Grande 2–3, Iguaçu 2; add the Petrópolis–Teresópolis traverse or the Ilha Grande circuit for full |
| Atacama + Uyuni | 6 | 8 | 9 | San Pedro 3–4 nights → the 3-day jeep tour ending in Uyuni → a spare Uyuni day (mirror effect and rain closures). La Paz +3 optional; leave Titicaca and the rest of Bolivia for May–Oct |
| Cuba | 8 | 10 | 14 | Havana 3, Viñales 3, Trinidad 4, Cienfuegos on the way; skip Santiago |
| Panama | 4 | 6 | 9 | Boquete 4, Panama City 2; San Blas +3 optional |
| Costa Rica | 1 | 3 | 5 | Backpackers mostly pass through: it's the dearest country on the route. A classic Costa Rica loop would be ~10 |
| Nicaragua | 10 | 14 | 21 | León 4, Granada 2, Ometepe 3–4, Somoto 1–2, San Juan del Sur 2 |
| Honduras | 6 | 8 | 10 | León → Copán transit 1, Copán 2, a night in La Ceiba, Utila 4 (a dive course takes ~4 days); Lake Yojoa +2 optional |
| **Total** | **55** | **74** | **101** | Without Cuba: 64 typical |

**Best route with Cuba (74 days plus travel, ≈14 Dec → 2 Mar):**

| ≈ Dates | Region | Days |
|---|---|---|
| 15 → 25 Dec | Cuba | 10 |
| 26 → 30 Dec | Brazil: Fortaleza → Jericoacoara | 4 |
| 30 Dec → 3 Jan | Brazil: Pipa, Recife/Olinda (New Year) | 4 |
| 3 → 11 Jan | Brazil: Salvador + Chapada Diamantina | 8 |
| 11 → 20 Jan | Brazil: Rio, Paraty, Iguaçu | 9 |
| 21 → 29 Jan | Atacama + Uyuni | 8 |
| 30 Jan → 5 Feb | Panama | 6 |
| 5 → 8 Feb | Costa Rica | 3 |
| 8 → 22 Feb | Nicaragua | 14 |
| 22 Feb → 2 Mar | Honduras | 8 |

- Any start from 1 to 14 Dec scores about the same. Starting on 1 Dec ends about 17 Feb.
- **Without Cuba (64 days plus travel):** Brazil on 2–27 Dec (Rio at Christmas), Atacama/Uyuni over New Year, then Panama → Costa Rica → Nicaragua → Honduras, ending about 6 Feb if you leave on 1 Dec. Any start from 1 to 20 Dec scores about the same.

**Cuba is CAUTION, close to NO-GO for budget independent travel (official sources, 21 Nov 2026):**
- US law still allows "Support for the Cuban People" travel. Since 30 Sep 2026, though, even indirect deals with Restricted List entities are banned (GAESA, CIMEX, Gaviota, many hotels). In practice that means private casas and private businesses only.
- US cards don't work. The UK says no foreign Visa or Mastercard works at all, so bring all your cash.
- Blackouts last up to 12 h a day in Havana. There's no jet fuel at the main airports through 1 Dec (the notice has been renewed monthly), and Havana–province buses fell from 419 a day to 11.
- The UK advises against all but essential travel, and Canada against non-essential travel.
- Entry: an eVisa (evisacuba.cu), the D'Viajeros form within 72 h of arrival, and an onward ticket.
- Copa flies Havana–Panama about 3 times a day, so Cuba connects through Panama.
- **Decide in early January**, against the airport fuel notices and the UK/Canada advisories.

**Getting around between regions:**
- **Brazil:** fly Recife → Salvador, Salvador → Rio and Rio → Foz do Iguaçu. Buses only for trips under 8 h, bought at the station (online booking needs a Brazilian tax ID).
- **Into Atacama:** fly to Calama via Santiago.
- **Out of Bolivia:** Uyuni → La Paz (flight ~$125 or bus ~$43), then Santa Cruz → Panama City (Copa or Boliviana). There's no direct La Paz–Panama flight.
- **Central America:**
  - South to north. Tica Bus Panama City → San José ($58, ~16 h); San José → Managua ($33).
  - **León → Copán:** a shuttle plus a boat across the Gulf of Fonseca via El Salvador, or a long day through Tegucigalpa. Shuttle from Copán to La Ceiba, a night in La Ceiba, then the morning ferry to Utila.
  - Transit through San Pedro Sula and Tegucigalpa only; don't stay there.

**Entry and advisories for US citizens:**

| Country | Entry | US advisory |
|---|---|---|
| Brazil | e-visa, $80.90, brazil.vfsevisa.com (flight booking + bank statement ≥ $2,000) | Level 2 |
| Chile | No visa | |
| Bolivia | No visa since 3 Dec 2025 | Level 2 |
| Panama | Onward ticket strictly enforced; $500 or proof of funds | Level 2 |
| Costa Rica | Return ticket (Tica Bus checks it) | Level 2 |
| Nicaragua | $10 stamp; email the migration form 7+ days ahead, to be safe | **Level 3**: may deny entry without explanation |
| Honduras | No visa | **Level 3** (Copán and the Bay Islands aren't singled out) |

**Costa Rica and Panama, wet-day %** (Dec / Jan / Feb / Mar):
- Guanacaste 30/18/**12**/21
- Central Valley 37/24/**18**/25
- Manuel Antonio 47/29/**25**/30
- Monteverde 69/60/49/**45**
- Arenal, Osa and the Caribbean coast 71–95% all window, with rainfall halving by Feb–Mar
- Panama City 62/32/**22**/34
- Pacific islands 73/38/**14**/18
- Boquete 55/36/30/**26**
- Bocas del Toro and San Blas 72–98%

**Big events:**
- **New Year in Rio** (Réveillon at Copacabana) fills beds and raises prices, so book early or spend it in Paraty or Salvador.
- **Carnival is ≈ 5–10 Feb 2027.** This draft has you in Central America then. Seeing Carnival in Brazil means pushing Brazil later, into the north-east's rainy season. That's the main trade-off to decide.

**Before booking, check:**
- Brazil's visa or e-visa rules for your passport (official site).
- Official security advisories for Honduras and Nicaragua.
- Border and shuttle routes, e.g. León → Copán and Copán → La Ceiba → Utila.

**Brazil, 10-year normals** (Tmax / wet-day %, Open-Meteo 2016–2025; reanalysis overstates coastal drizzle days, so compare places with each other):

| Place | Dec | Jan | Feb | Mar |
|---|---|---|---|---|
| Lençóis Maranhenses | 30° 39% | 28° 80% | 28° 93% | 28° 95% |
| Jericoacoara | 32° 41% | 30° 75% | 29° 88% | 29° 96% |
| Fortaleza | 30° 44% | 30° 73% | 29° 86% | 29° 91% |
| Pipa / Natal | 29° 64% | 29° 71% | 30° 74% | 29° 78% |
| Recife / Olinda | 29° 66% | 29° 70% | 29° 73% | 29° 81% |
| Salvador | 29° 50% | 29° 63% | 29° 58% | 29° 63% |
| Chapada Diamantina | 31° 50% | 31° 59% | 31° 58% | 31° 55% |
| Rio de Janeiro | 29° 48% | 30° 47% | 30° 48% | 29° 42% |
| Paraty / Ilha Grande | 29° 69% | 30° 77% | 30° 78% | 29° 69% |
| Florianópolis | 27° 52% | 29° 68% | 29° 63% | 28° 60% |
| Foz do Iguaçu | 31° 46% | 31° 54% | 31° 45% | 30° 43% |
| Bonito / Pantanal | 31° 55% | 31° 56% | 31° 61% | 31° 48% |
| Manaus (Amazon) | 29° 84% | 30° 76% | 29° 81% | 29° 83% |

**Other never-visited places:**

| Place | Dec | Jan | Feb | Mar |
|---|---|---|---|---|
| San Pedro de Atacama (CL) | 28° 2% | 28° 11% | 27° 20% | 27° 5% |
| Uyuni (BO) | 20° 29% | 18° 55% | 18° 54% | 18° 31% |
| Santiago (CL) | 29° 3% | 30° 2% | 30° 4% | 28° 3% |
| León (NI) | 33° 14% | 34° 7% | 35° 3% | 36° 8% |
| Ometepe (NI) | 28° 68% | 28° 48% | 29° 41% | 30° 38% |
| Boquete (PA) | 23° 55% | 24° 36% | 24° 30% | 25° 26% |
| Copán (HN) | 25° 50% | 25° 40% | 27° 42% | 29° 35% |
| Utila (HN) | 27° 73% | 26° 58% | 27° 42% | 27° 30% |
| Havana (CU) | 27° 22% | 26° 31% | 28° 24% | 29° 21% |

## What carries over from Europe 2026

- **Traveller and style:** solo male, budget, nature and hiking first, free sights first, no churches, food from locals' places, a craft beer in each city.
- **Getting around:** the best surface transport first (trains in Europe; in Latin America that will mostly mean long-distance buses). Rank legs on journey time and price, and buy from the operator's own site where possible.
- **Beds:**
  - Sorting rules: no party hostels, bed privacy curtains, a kitchen where eating out is expensive.
  - Compare **checkout totals** on Booking, Agoda, Hostelworld and the property's own booking site.
  - Read the full review spread.
  - See the [lessons](../europe-2026/README.md#lessons-worth-reusing).
- **Tools:** the API-first booking and fare recipes in [`AGENTS.md`](../../AGENTS.md); Google Maps lists with visible notes, plus icon lists for walks, hikes and bike routes ([`skills/google-maps-saved-places`](../../skills/google-maps-saved-places/)); and AI Mode research for leads ([`skills/google-ai-mode-research`](../../skills/google-ai-mode-research/)).
- **Flights:** sweep every practical gateway for cash and award fares, and book budget one-ways the moment the decision is made. See [flights: points vs cash](../../research/flights-points-vs-cash.md).

## To research

- [ ] Countries and the overall direction of the route (what's already been visited, and what's fresh)
- [ ] Seasons and weather by region and month: rainy seasons, altitude, hurricane season
- [ ] Entry rules: visa or e-visa, maximum stay per country, onward-ticket requirements, reciprocity fees
- [ ] Budget per day by country, and the cash/ATM/card situation. Build it the way the [Europe budget forecast](../europe-2026/budget-forecast.md) was built, adjusted for the [lessons from what Europe actually cost](../europe-2026/budget-actual.md#lessons-for-the-next-budget): lodging + food + drinks + local costs per region, a 10% cushion, then transport, sights, insurance
- [ ] Transport backbone: long-distance bus networks and booking sites, any passenger trains, regional budget airlines, border crossings
- [ ] Safety by city and route, including night buses
- [ ] Health: vaccinations, altitude, water
- [ ] Hiking: the multi-day treks worth planning around (permits and seasons), and day hikes reachable by public transport
- [ ] Gear changes compared with the [Europe packing list](../../research/packing-list.md)
