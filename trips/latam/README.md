# Latin America: next leg (planning)

**Status:** planning. Window: **December → mid-March**.

**Route v5 (24 Nov 2026), now the working plan:** [skeleton with dates, legs and costs](route-v5-brainstorm.md#15-route-v5-locked-skeleton-user-24-nov-santiago-dropped-panama-kept) · [route map](latam-route-draft.svg) · [how it was chosen](route-v5-brainstorm.md).
- ✈ Seattle → Rio on Day 0 (Alaska business award); **Day 1 = Tue 8 Dec 2026**. The plan counts trip days from there (see the [itinerary](itinerary.md)).
- Rio → Ilha Grande → Paraty → São Paulo → Curitiba → Iguaçu → Florianópolis → Porto Alegre.
- Punta del Diablo → Cabo Polonio → Montevideo (New Year) → Colonia → Buenos Aires. (Paraguay was dropped on 27 Nov.)
- Córdoba (+ Los Gigantes, Champaquí) → Cafayate → Salta → Quebrada de Humahuaca → San Pedro de Atacama → jeep tour to Uyuni.
- Potosí → Sucre → ✈ La Paz → Titicaca → Colca → Arequipa.
- ✈ Panama City → Boquete → Chirripó → Uvita → Monteverde → Arenal → Rincón → San Juan del Sur → Ometepe → Granada → León → Estelí (+ Somoto).
- ✈ home from Managua on Day 95, with 3 spare days before mid-March.

**[Day-by-day itinerary for v5](itinerary.md)** (the index) with one guide per stop in [`guides/`](guides/): beds, buses and flights checked live on 24 Nov 2026. Nothing is booked. [Budget forecast](budget-forecast.md): ≈ $6.8–7.4k expected, carry ≈ $8.2k.

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

## How the route was chosen

[route-v5-brainstorm.md](route-v5-brainstorm.md) records how v4 (full Brazil incl. the north-east and Bahia) became v5, section by section:
- the route models and weather data;
- South America first vs Central America first;
- Rio vs Santiago entry;
- Bahia and the no-backtracking rule;
- Córdoba instead of Mendoza;
- dropping Santiago and keeping Panama;
- the adventure-hub sweep;
- how other travellers route it;
- the leg-by-leg transport table and the award flights.

The v4 write-up is in git history. Models: [`tools/route-optimizer/`](../../tools/route-optimizer/) (`brainstorm_v5.py`).

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

- [x] Countries and the overall direction of the route: v5, [brainstorm](route-v5-brainstorm.md)
- [x] Seasons and weather by region and month (10-year normals, corrected with station data for the Andes)
- [x] Entry rules: Brazil e-visa, yellow fever (Paraguay, Bolivia, Panama, Costa Rica), onward tickets (Panama, Costa Rica), Nicaragua pre-registration. See the [book-first list](itinerary.md#book-these-first-they-sell-out-or-need-you)
- [x] Budget per day by country, and the cash/ATM/card situation: [budget-forecast.md](budget-forecast.md).
- [x] Transport backbone: every leg priced and linked in the [guides](guides/)
- [ ] Safety by city and route, including night buses
- [ ] Health: vaccinations, altitude, water
- [x] Hiking: adventure hubs and treks on the route ([brainstorm §10](route-v5-brainstorm.md), the guides)
- [ ] Gear changes compared with the [Europe packing list](../../research/packing-list.md)
