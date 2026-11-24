# Latin America: next leg (planning)

**Status:** planning. Window: **December → mid-March**.

**Brazil leg (Plan B, 3 Dec – ~2 Jan): [day-by-day itinerary](itinerary.md) · [budget forecast](budget-forecast.md) · [route map draft](latam-route-draft.svg).** Prices checked live on 24 Nov 2026; nothing booked. The rest of the route (Uruguay, Paraguay, Santiago/Salta, the Andes, Central America) is still being decided.

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

## Draft route v4 (21 Nov 2026): consensus days, 2-week floating buffer, no Cuba

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
| Panama | 4 | 6 | 9 | Boquete 4, Panama City 2; San Blas +3 optional |
| Costa Rica | 3 | **10** | 14 | A real stop while it's in season: Arenal, Monteverde, Manuel Antonio, Guanacaste. Backpackers who only pass through give it ~3 (it's the dearest country on the route) |
| Nicaragua | 10 | 14 | 21 | León 4, Granada 2, Ometepe 3–4, Somoto 1–2, San Juan del Sur 2 |
| Honduras | 6 | 8 | 10 | León → Copán transit 1, Copán 2, a night in La Ceiba, Utila 4 (a dive course takes ~4 days); Lake Yojoa +2 optional |
| **Total** | **50** | **71** | **96** | |

**Best route (71 days plus travel, ≈1 Dec → 13 Feb):**

| ≈ Dates | Region | Days |
|---|---|---|
| 2 → 6 Dec | Brazil: Fortaleza → Jericoacoara | 4 |
| 6 → 10 Dec | Brazil: Pipa, Recife/Olinda | 4 |
| 10 → 18 Dec | Brazil: Salvador + Chapada Diamantina | 8 |
| 18 → 27 Dec | Brazil: Rio, Paraty, Iguaçu (Christmas in Rio) | 9 |
| 28 Dec → 5 Jan | Atacama + Uyuni (New Year) | 8 |
| 6 → 12 Jan | Panama | 6 |
| 12 → 22 Jan | Costa Rica (Guanacaste ~8 mm of rain in January) | 10 |
| 22 Jan → 5 Feb | Nicaragua | 14 |
| 5 → 13 Feb | Honduras | 8 |

- Any start from 1 to 18 Dec scores about the same. Leaving on 1 Dec leaves **31 days free**: the 14-day buffer plus 17 days to start later or come home earlier.
- Spending buffer days early pushes Costa Rica into February, its driest month.

**Cuba: dropped.** US law bans tourist travel to Cuba. A trip is legal only under an OFAC general license category such as "Support for the Cuban People", which requires a full-time schedule of engagement with Cubans and records kept for 5 years. A sightseeing, hiking and beach trip doesn't fit. The situation on the ground points the same way: all-cash, daily blackouts, jet-fuel shortages, and UK and Canadian advice against travel.

**Other Caribbean islands (Dec–Mar is the dry season on all of them):**
- **Dominican Republic (optional, +7 days):** a new country, the cheapest big island, Pico Duarte (2–3-day hike), humpback whales at Samaná from mid-January to March. Seattle → Santo Domingo was $373 via Newark. Fitted as the December opener, it ends the trip about 27 Feb, with about 3–4 more expected rainy days than starting in Brazil.
- **Lesser Antilles** (Guadeloupe → Dominica → Martinique → St Lucia by ferry): the Caribbean's best hiking, but euro and resort prices, and off the route. Better as a trip of its own.
- **Puerto Rico:** easy from the US at any time. Better as a trip of its own.
- **Trinidad & Tobago:** Carnival on 8–9 Feb 2027.
- **San Andrés / Providencia, the Corn Islands, Utila:** wet in December, driest in Feb–Mar.

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
