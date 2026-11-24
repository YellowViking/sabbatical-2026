# LatAm route v5: brainstorm (24 Nov 2026)

v5 cuts Brazil to the **Rio–São Paulo corridor**. The trip then heads south and west, up into the Andes, and finishes in Central America. Brazil's north-east and Bahia move to a separate Sep–Nov trip, when they're dry and uncrowded and the Pantanal, Bonito and Lençóis Maranhenses are also in season. v4 (the full Brazil plan) stays on branch `latam-route-v4`.

Model: [`tools/route-optimizer/brainstorm_v5.py`](../../tools/route-optimizer/brainstorm_v5.py). It uses typical (consensus) days only and keeps a 14-day floating buffer. It scores:
- the value of each new country;
- expected wet days, from 10-year normals (Open-Meteo 2016–25);
- crowd and price peaks: Brazil's school holidays and Carnival (20 Dec – 10 Feb), Uruguay's high season (24 Dec – 15 Feb), and Central America's Christmas–New Year (20 Dec – 5 Jan);
- distance moved.

## 1. South America first, or Central America first?

**South America first**, in every variant tested.

| Order | Score | Wet days | Peak-season days |
|---|---|---|---|
| **South America first, entering Rio** | **5.5** | **29.4** | **0** |
| Central America first | −6.8 | 32.9 | 12 |
| (weather only, peaks ignored) | 6.4 vs −0.8 | | |

Share of days with rain (≥ 1 mm), December vs February:

| Region | Dec | Feb | Best month for it |
|---|---|---|---|
| Atacama + Uyuni | 16% | 37% | **Dec** |
| S Peru (Arequipa, Colca) | 38% | 80% | **Dec** |
| Titicaca | 80% | 93% | **Dec** |
| Bolivia cities | 69% | 78% | **Dec** |
| Nicaragua | 41% | 22% | **Feb** |
| Costa Rica | 67% | 50% | **Feb** |
| Panama | 63% | 22% | **Feb** |

The two halves of the trip have opposite seasons:
- **The Andes:** their rainy season builds from December to a February peak.
- **Central America:** its dry season starts in late December and is driest in February–March.

Going Central America first puts both halves in their worse months. It also lands Costa Rica on Christmas–New Year (its dearest fortnight) and leaves the Rio corridor for late February, the hottest weeks, around Carnival (5–10 Feb 2027).

Smaller pluses for South America first:
- The long flight comes at the start.
- The trip ends a 5–7 h flight from home.
- Semana Santa (21–28 Mar 2027) falls after the window closes.

## 2. Fly into Santiago (SCL) or Rio (GIG)?

Award flights on Alaska Atmos, from Seattle, checked live on 24 Nov:

| Arrive | Points + tax | Fastest at that price | Seats | Cash, 1–3 Dec |
|---|---|---|---|---|
| **Santiago** | 30,000 + $26 | **14.6 h**, 1 stop: AA767 SEA–DFW 12:37, AA945 DFW–SCL 19:40 → 08:15 (3 and 5 Dec) | 9 | $625 |
| Rio | 30,000 + $26 | 17.2–19 h, 2 stops via MIA: AA905 MIA–GIG 22:55 → 09:25 (2–4 Dec) | 9 (only **1** at 30k on 3 Dec) | $565–578 |

Santiago is 3–4 h faster for the same points. However, the route needs Brazil first, before its holidays start on about 20 Dec, and Brazil is the far east end of the loop:

| Entry | Score | What it costs |
|---|---|---|
| **Rio, then the corridor → Iguaçu → Paraguay → Uruguay → ✈ Santiago → Andes** | **5.5** | 3 flights in total (SEA→Rio, Montevideo→Santiago ~$166, Lima→Central America) |
| Santiago, then fly to Rio (SCL→GIG $168–233 in Dec) | −0.9 | An extra flight and travel day; Uruguay slides into Christmas week; every Andes stop is about 5 days later and wetter |
| Santiago, then overland east (Uruguay → Paraguay → Iguaçu → Rio) | 0.0 | Brazil lands on 20–29 Dec: peak heat, crowds and prices |
| Santiago, then the Andes first, Brazil last | −9.2 | Brazil in mid-January plus a long backtrack |

**Verdict: enter at Rio.** Santiago only wins if Brazil is dropped entirely, because the Andes and Central America alone start naturally there. Brazil-to-Andes flights for reference, late Dec: Rio→Salta $172–321, Rio→Calama $213–242, Rio→Santa Cruz $223–291, Rio→La Paz $282+.

## 3. What the model fits (≤ 91 typical days, ends ≈ 2 Mar, 14-day buffer left)

The best plan uses 89 days, has 0 peak-season days, and drops Buenos Aires, Salta/Jujuy and Panama:

| ≈ Dates | Region |
|---|---|
| 2 → 11 Dec | Rio → Ilha Grande → Paraty → São Paulo |
| 11 → 14 Dec | Curitiba (Serra Verde train) → Iguaçu |
| 14 → 18 Dec | Paraguay: Asunción, Encarnación |
| 18 → 24 Dec | Uruguay: Colonia, Montevideo, Cabo Polonio |
| 24 → 27 Dec | Mendoza |
| 27 Dec → 1 Jan | Santiago, Valparaíso (New Year) |
| 1 → 9 Jan | San Pedro de Atacama + Uyuni |
| 9 → 16 Jan | Sucre, Potosí, La Paz |
| 16 → 19 Jan | Titicaca |
| 19 → 23 Jan | Arequipa, Colca |
| 23 → 28 Jan | Peru coast → Lima |
| 29 Jan → 8 Feb | Costa Rica |
| 8 → 22 Feb | Nicaragua |
| 22 Feb → 2 Mar | Honduras (Copán, Utila) |

**Open:**
- Salta/Jujuy, Buenos Aires, Panama vs Honduras: which to keep.
- Mendoza before or after Santiago.
- How to get from Santiago to San Pedro: fly to Calama, or bus via Salta.

## 4. A friend's tips (24 Nov): what fits

The model now sets Mendoza at 5 days and keeps Salta/Jujuy in. Optional Bahia blocks were added and tested.

| Plan | Score | Peak-season days | Ends | Buffer left |
|---|---|---|---|---|
| **A: corridor → Iguaçu → Paraguay → Uruguay (18–24 Dec) → Santiago → Mendoza 5 d → Salta/Jujuy → Atacama/Uyuni → Bolivia → Lima → Panama → Costa Rica → Nicaragua** | **5.3** | **0** | 2 Mar | 14 |
| B: Bahia first (✈ Rio→Salvador on arrival $132–157; Salvador, Boipeba/Morerê, Chapada; ✈ Salvador→Rio 12–13 Dec $109–112), then A | 3.3 | 10 | 12 Mar | **4** |
| B2: as B, but drop Panama + Peru coast to keep the buffer | −3.3 | 10 | 1 Mar | 14 |
| C: Rio first, ✈ São Paulo→Salvador, Bahia, ✈ Salvador→Iguaçu | 0.2 | 10 | 13 Mar | 3 |

The pull of B and C is real: Morerê's quiet window is before about 20 Dec, and both put Bahia there. They also shift everything after it about 10 days later:
- Rio–São Paulo and Iguaçu run into the Brazilian holidays.
- **Uruguay lands on New Year**, Cabo Polonio's busiest week.
- The Andes block slides further into the wet season.

**Mendoza:** Vallecitos (Cordón del Plata) gets one day.
- The trailhead is the old ski-centre car park at about 3,000 m.
- Las Veguitas is about 5 km and easy (Luján de Cuyo tourism page). Longer peaks reach about 4,200 m.
- There is no bus to the trailhead. Take a bus to Potrerillos, then a transfer or a refuge shuttle.
- It doubles as acclimatisation before Salta and Atacama.

**Amazon:** skipped here, since it's already done in Ecuador. The on-route option is the Rurrenabaque pampas from La Paz: a 40-min flight plus a 3-day tour. It's open-savanna wildlife, unlike Ecuador's rainforest, but January flights are often cancelled. Treat it as a buffer-funded maybe, decided in La Paz.

## 5. Montevideo → Santiago overland, with Córdoba instead of Mendoza

Mendoza is already visited, so it becomes a transit night. The new stop is **Córdoba + the Sierras de Córdoba**, a new region. The $175 Montevideo → Santiago flight is replaced by land legs, plus a $43–88 domestic hop from Santiago to Calama:

| ≈ Dates | Leg / stop |
|---|---|
| 18 → 23 Dec | Uruguay. Enter from Paraguay via Posadas → Concordia → Salto (or the direct Wed/Sat bus from Encarnación), then Montevideo → Cabo Polonio → Colonia |
| 23 Dec | Ferry Colonia → Buenos Aires ($50–95; reduced sailings on 24, 25 and 31 Dec), then an overnight bus to Córdoba (≈ 10 h) |
| 24 → 29 Dec | **Córdoba + Sierras**: city 1–2 nights (Aldea Hostel 9.5/1,137 reviews, ≈ $15 dorm), then a Sierras base |
| 29 → 30 Dec | Overnight bus Córdoba → Mendoza (≈ 10–11 h), then the **day bus over the Andes** to Santiago (7½–9 h, $25–50; take the 7–8 am bus because of summer queues at the border) |
| 30 Dec → 4 Jan | Santiago + Valparaíso (New Year) |
| ≈ 5 Jan | ✈ Santiago → Calama ($43–51 on 5–10 Jan), then 1½ h bus to San Pedro |
| then | San Pedro → bus via Paso de Jama → Jujuy/Salta/Cafayate → La Quiaca/Villazón → Tupiza → 4-day jeep tour to Uyuni → Bolivia |

**Córdoba, the free outdoors:**
- **Quebrada del Condorito NP:** free entry (official park page, "Acceso gratuito"). The COATA bus on the Altas Cumbres road stops at La Pampilla. Balcón Norte is ~10–12 km and needs no guide.
- **Los Gigantes:** via Tanti.
- **Cerro Uritorco:** above Capilla del Monte; the trail is privately run and charges a fee.
- **La Cumbrecita:** car-free village, via Villa General Belgrano.
- **Cerro Champaquí (2,790 m):** 2-day trek. No guide is needed, but there is a compulsory online risk-zone declaration.

**Weather:**
- Córdoba: rain on 31% of December days. The Sierras: 36–38%, as afternoon storms, so hike in the mornings.
- Mendoza, for comparison: 14%.
- That is the whole score gap: 3.2 here vs 5.3 for the Mendoza version.

**Alternatives looked at and rejected:**
- **San Juan (Barreal, Ischigualasto):** drier, but 59% of December days in San Juan reach 33 °C or more. There is no bus into the parks, Ischigualasto charges foreigners ≈ ARS 65,000, and Hostelworld has no beds in Barreal.
- **Paso de Agua Negra to the Elqui Valley:** not expected to open before January 2027, and only small minibuses use it.
- **San Luis (Merlo, Quijadas):** no bus to Quijadas.
- **Uspallata (Aconcagua):** dry and cool, and on the Santiago road. It's still a possible one-night break on the crossing, but Hostelworld has nothing there.

## 6. Titicaca and Arequipa/Colca: wet, or a bad input?

They were dropped mainly because of a **bad input**. The weather data came from reanalysis (Open-Meteo), a model estimate on a ~25 km grid. Over the dry Andes it overstated rain badly. Station normals:

| Place | Rain (Dec / Jan / Feb), station | Reanalysis had | Source |
|---|---|---|---|
| **Arequipa city** | **4 / 28 / 36 mm**, ~18 rain days in the *whole year* | 21 / 102 / 169 mm, rain on 46% of January days | WMO, via Wikipedia |
| Colca (Chivay) | 54 / 115 / 117 mm | Cabanaconde 87 / 247 / 266 mm | Wikipedia climate table |
| Titicaca (Copacabana) | 109 / 185 / 113 mm on 13 / 19 / 14 days (42 / 63 / 49% of days) | 81 / 87 / 93% of days | SENAMHI Bolivia, via Wikipedia |
| La Paz (control) | 95 / 134 / 105 mm on 16 / 21 / 16 days | 60 / 67 / 69% | matches |

- **Arequipa** is desert; January isn't a problem there.
- **Colca** really is in its rainy season in late January. In the hourly data, most of the rain falls in the afternoon: 67% of January mornings are dry (< 0.5 mm, 06–13 h). That suits the 5 am climb out of the canyon.
- **Titicaca** is the wettest stop on the route, with rain on about 19 January days. It's a short stop, and the Isla del Sol walk is a morning walk.

The other reason was the **91-day cap**:
- Peru counts as a visited country (value 0.8 vs 1.0), and Panama (new, driest in February) narrowly beat these stops.
- The model also didn't know that the bus from La Paz to Lima runs **through** Copacabana, Puno and Arequipa anyway.

With station normals in the model (`brainstorm_v5.py`), Titicaca stays. Keeping Titicaca, Arequipa/Colca, Córdoba and Salta/Jujuy all together drops the **Peru coast (Huacachina, Paracas; Lima is already visited), Panama and Honduras**. The plan then ends on ≈ 26 Feb with the 14-day buffer intact plus a few spare days. The exit flight leaves from Arequipa: AQP → San José $263 (1 and 5–8 Feb) vs LIM → San José $252.

## 7. Bahia, with alternating scenery (user, 24 Nov: "alternate sceneries, don't want all beaches")

**Bahia lite = Salvador (city) + Chapada Diamantina (mountains).** Morerê/Boipeba is left out because it duplicates Ilha Grande: both are car-free tropical islands with reef pools and trails between beaches. Ilha Grande is already on the route and has the better hiking (Papagaio, the circuit). Paraty also goes once Bahia is in: Salvador's Pelourinho covers the colonial-town side and Ilha Grande covers the beaches.

| Date | Leg / stop | Scenery |
|---|---|---|
| Fri 4 Dec | Arrive GIG 09:25, ✈ Rio → Salvador ($157; $132 on 5 Dec) | |
| 4 → 6 Dec | Salvador | colonial city, Afro-Brazilian culture |
| Sun 6 Dec | Rápido Federal 08:00 → Lençóis 14:40 (also 13:00, 23:00) | |
| 6 → 10 Dec | Lençóis / Chapada Diamantina | table mountains, canyons, waterfalls |
| Thu 10 Dec | Overnight bus 23:00 → Salvador 06:00, ✈ Salvador → Rio Fri 11 Dec ($112) | |
| 11 → 15 Dec | Rio | city + granite peaks (Tijuca, Pedra da Gávea) |
| 15 → 17 Dec | Ilha Grande | island jungle trails + beaches (the one Brazilian beach stop) |
| 17 → 19 Dec | São Paulo | megacity |
| then | Curitiba → Serra Verde train → Iguaçu → Paraguay → Uruguay → Córdoba → … | Atlantic forest, waterfalls, … |

Model: score −1.7 vs 0.6 without Bahia. It costs 7 days in holiday peaks and leaves **13 buffer days instead of 18**. There are 2 extra flights (≈ $270). Uruguay lands on 23–29 Dec, so do Cabo Polonio before ~27 Dec, when the New Year crowds arrive.

**Scenery along the whole route:**

| # | Stop | Scenery |
|---|---|---|
| 1 | Salvador | colonial city |
| 2 | Chapada Diamantina | mountains, canyons |
| 3 | Rio | city + peaks |
| 4 | Ilha Grande | **beach** + jungle |
| 5 | São Paulo | megacity |
| 6 | Serra Verde train, Iguaçu | Atlantic forest, waterfalls |
| 7 | Asunción, Encarnación | city, Jesuit ruins |
| 8 | Salto, Montevideo | hot springs, city |
| 9 | Cabo Polonio | **beach**, dunes |
| 10 | Colonia, Córdoba + Sierras | colonial town, hills |
| 11 | Andes crossing, Santiago, Valparaíso | high mountains, city, Pacific port |
| 12 | San Pedro de Atacama | desert |
| 13 | Purmamarca/Jujuy, Salta, Cafayate | coloured canyons, city, vineyards |
| 14 | Tupiza → Uyuni | canyons, lagoons, salt flat |
| 15 | Potosí, Sucre, La Paz | colonial and mining cities, mountain city |
| 16 | Titicaca | lake, islands |
| 17 | Arequipa, Colca | colonial city, canyon |
| 18 | Costa Rica | volcanoes, rainforest, cloud forest, one **beach** |
| 19 | Nicaragua | colonial cities, volcanoes, lake island, one surf **beach** |

There are four beach stops in three months, and no two are back to back. The one long run of similar scenery is **12–14: about two weeks of high desert and red canyons**. Break it with Salta city. Don't buy San Pedro's lagoon or geyser tours, because the Tupiza → Uyuni jeep tour covers the same sights (Sol de Mañana geysers, Lagunas Colorada and Verde). Use San Pedro for Valle de la Luna by bike and the night sky.

## 8. Backtracking audit (user, 24 Nov: "routing optimal is important, avoid backtracking")

**Bahia (section 7) is withdrawn.** Rio → ✈ Salvador → Chapada → bus back to Salvador → ✈ Rio is an out-and-back of about 2,600 km. Bahia lies 1,200 km north of a route that otherwise runs south and then west, so every version doubles back except one: **enter Brazil at Salvador**. That entry costs:
- **Flight in:** SEA → Salvador is cash only, $631 on 3 Dec. Alaska has no award space to Salvador, against 30k points + $26 to Rio.
- **Leaving Chapada:** Lençóis → Belo Horizonte by bus takes 24–30 h, via Seabra and Montes Claros. The alternative is Azul's Thursday flight, $138, which itself connects through Salvador.
- **Then** Belo Horizonte → Rio.
- **Overall:** +≈ 8 days, the Rio corridor moves into the holidays, Uruguay lands on New Year, and the buffer shrinks to ≈ 10.

**Verdict:** keep Bahia, Morerê and Chapada for a Sep–Nov trip to Brazil's north-east, together with Lençóis Maranhenses, the Pantanal and Bonito.

**The route without Bahia, leg by leg:**

| Leg | Direction | Repeats ground? |
|---|---|---|
| ✈ Seattle → Rio (Alaska 30k + $26) | | |
| Rio → Ilha Grande → Paraty → São Paulo → Curitiba (Serra Verde train) → Iguaçu | south-west | no |
| Iguaçu → Ciudad del Este → Asunción → Encarnación → Posadas | west, then south-east (a triangle) | no |
| Posadas → Concordia → Salto → Montevideo | south | no |
| Montevideo → **Cabo Polonio** → Montevideo | east and back | **yes, ≈ 4 h spur** |
| Montevideo → Colonia → ferry → Buenos Aires (or Buquebus direct, 2 h 45) | west | no |
| Buenos Aires → Córdoba → Mendoza → over the Andes → Santiago/Valparaíso | west | no |
| ✈ Santiago → Calama ($43–88) → San Pedro → Paso de Jama → **Salta** | north, then east | Salta sits ≈ 2 h south of the line, so Salta ↔ Jujuy is passed twice |
| Salta (**Cafayate as a day tour**) → Jujuy → Purmamarca/Tilcara/Humahuaca → La Quiaca → Tupiza | north | no |
| Tupiza → 4-day jeep tour → Uyuni → Potosí → Sucre | north-east | no |
| ✈ **Sucre → La Paz $50** (daily) instead of the overnight bus back through Potosí | north-west | no |
| La Paz → Copacabana → Puno → **4M Express via Colca** (overnight in Chivay) → Arequipa | north-west | no; Colca is on the way, not a spur from Arequipa |
| ✈ Arequipa → San José $263 | | |
| Costa Rica → Nicaragua, fly home from Managua | north | no |

Only two short repeats are left, Cabo Polonio (≈ 4 h) and Salta–Jujuy (≈ 2 h). Both are spurs to a single destination, not retraced legs.

## 9. Entry flight in business, with the US legs in first (checked 24 Nov)

**Alaska Atmos: 60,000 points + $26, Seattle → Rio.** These options are first class on every US leg and lie-flat business MIA → GIG. Cash for the same American Airlines trip is about $4,063 (Google Flights, 3 Dec), so that's about 6.7¢ a point. Economy is 30,000 + $26.

| Leave Seattle | Route | Total time | Seats | Arrive Rio |
|---|---|---|---|---|
| **Mon 7 Dec 09:15** | AA771 SEA–PHL (A321neo, F) → AA688 PHL–MIA 18:00 (**787-8, lie-flat F**) → AA905 MIA–GIG 22:55 (777-200, lie-flat J) | 19.2 h | 3 | Tue 8 Dec 09:25 |
| Mon 7 Dec 06:20 | AA2273 SEA–ORD (F) → AA1201 ORD–MIA (F) → AA991 MIA–GIG 19:55 (787-8, J) | 19.2 h | 3 | Tue 8 Dec 06:30 |
| Sun 6 Dec 07:30 | AA737 SEA–DFW (A321neo, F) → AA1199 DFW–MIA (F) → AA905 (J) | 20.9 h | 1 | Mon 7 Dec 09:25 |
| Tue 8 Dec 06:00 | AA3068 SEA–CLT (F) → AA574 CLT–MIA (**777, lie-flat F**) → AA991 (J) | 19.5 h | 1 | Wed 9 Dec 06:30 |
| Thu 3 Dec 06:00 | AA3068 SEA–CLT (F) → AA574 CLT–MIA (777, F) → AA905 (J) | 22.4 h | 1 | Fri 4 Dec 09:25 |
| Sat 5 Dec 23:39 | AA2379 SEA–ORD red-eye (F) → AA1875 ORD–MIA (F) → AA905 Sun 22:55 (J), 11 h in Miami | 28.8 h | 2 | Mon 7 Dec 09:25 |

On 1, 2 and 4 Dec no business seats are open. A cheaper-looking 18 h option on 8 Dec (LAX → MIA arriving 19:08 for the 19:55) has only a 47-min connection in Miami.

**United (Chase points) is not worth it:**
- Polaris via Houston with first-class US legs is 295,000–395,000 miles (Standard).
- The 88,000-mile "business" saver is Avianca A320 recliners via Bogotá, with economy US legs.

## 10. Adventure hubs along the route ("like Huaraz"), web sweep 24 Nov

Sources: Google AI Mode sweeps per region (Reddit/blog consensus, Wikivoyage, operator and park sites), Hostelworld's listings API on the planned dates, and the CONAF and SINAC rules as quoted in those summaries (to confirm on the official pages before booking).

The consensus "Huaraz-like" towns for Dec–Feb are El Chaltén, Bariloche, Puerto Natales (all Patagonia, already done), **Pucón** and **San Pedro de Atacama**. Bolivia and southern Peru are in their rainy season. Morning hikes work there, but most agencies pause the 5–6,000 m climbs.

**A. On the route, little or no detour**

| Hub | Where it sits | Adventure | Season on our dates | Cost / access | Extra days |
|---|---|---|---|---|---|
| **Teresópolis (Serra dos Órgãos)** | Straight from GIG airport, before Rio city: GIG → Teresópolis → Rio → Ilha Grande, no repeats | Brazil's climbing and trekking hub: Pedra do Sino, Dedo de Deus views, the Petrópolis–Teresópolis traverse (3 d) | Dec: afternoon storms, so start at 7 am | Bus Rio → Teresópolis 2 h, 16 a day; small park fee; free trails outside the gate | +2 |
| **Sierra de las Ánimas** (Uruguay) | On the Montevideo → Cabo Polonio highway, 1.5 km walk from the bus stop | Ridge day hike, rock pools | Dec fine (hot) | Coastal buses | 0 |
| **Los Gigantes** (Córdoba) | Inside the Córdoba days | 2–3 day unguided traverse, Club Andino refuge, scrambling | Afternoon storms | Sarmiento bus to Casas Nuevas (1–2 a day); register at the trailhead | 0 |
| **Potrerillos / Vallecitos** (Mendoza) | On the road from Mendoza to Chile; it replaces the Mendoza city night | Cordón del Plata hikes to ~4,200 m, Río Mendoza rafting | Dry (14% wet days) | Bus Mendoza → Potrerillos 1 h, then a transfer up | +1 |
| **Cajón del Maipo** (Santiago) | Short spur from Santiago, which the Calama flight leaves from anyway | **El Morado glacier hike** (12–15 km), Baños Morales hot pools, Valle Colina | Prime season (dry) | Metrobús 72A daily in summer, ~2.5 h, about CLP 5,000; El Morado CLP 9,300, booked on Pases Parques, **closed Mondays**, last entry 12:30 | +2 |
| **San Pedro de Atacama** | On the route | **Cerro Toco 5,604 m** (non-technical walk-up), Láscar 5,592 m | Clear mornings; afternoon cloud from January | Toco ≈ $110–150 guided (no buses to trailheads) | +1 |
| **Tupiza** | On the route | Red canyon treks, horse riding; the start of the 4-day Uyuni tour | Drier rain-shadow valley | — | 0 |
| **La Paz: Condoriri / Pico Austria 5,320 m** | Out from La Paz and back | 2-day non-technical summit, glacier lagoon | January: summit in the morning, sleet in the afternoon | Agency trip | +2 |
| **Colca (Cabanaconde → Sangalle)** | On the route (Puno → Chivay → Arequipa) | Self-guided canyon trek | Wet but open; climb out at 5 am | Boleto turístico S/70 | 0 |
| **San Gerardo de Rivas (Chirripó 3,820 m)**, Costa Rica's Huaraz | Start Costa Rica in the south, then go north up the Pacific side | 2-day climb with a night at Base Crestones | Feb is peak dry season | SINAC ≈ $18/day + Crestones bunk (60 a night), **February dates are already on sale**; the park closes the last weekend of Feb for a race | in CR days |
| **León + Ometepe + Somoto** (Nicaragua) | South → north through Nicaragua | Cerro Negro boarding, Telica overnight, Concepción, Somoto canyon ($20–30) | Dry | Cheap | in NI days |
| **Gracias / Celaque** (Honduras), Honduras's Huaraz | Straight on north from Somoto via El Espino, then fly home from San Pedro Sula | Cerro Las Minas 2,870 m, 1–3 days; Lake Yojoa | Dry | Park < $10 | only if Honduras returns |

**B. Big hubs that need a route change**
- **Pucón** (Villarrica climb $130–180 guided, Huerquehue, rafting), Chile's Huaraz. A linear way in: Córdoba → Neuquén → San Martín de los Andes → Mamuil Malal pass → **Pucón** → overnight bus → Santiago. That replaces the Mendoza crossing and adds ≈ 3–4 days; the summer bus over the pass still needs confirming. Pucón has 13 places on Hostelworld for 30 Dec (Soley Hostel 9.7, $21).
- **Torotoro** (canyons, dinosaur tracks): Sucre → Cochabamba → Torotoro → La Paz, instead of the $50 flight. Caves close when flooded in January. Adds ≈ 3 days.
- **Skip:** Sajama (spur), Iruya (dirt road washes out in January), Sorata (muddy, cloudy in January), the Arequipa volcano climbs (agencies pause them Jan–Mar), Brotas and Bonito (all paid and agency-only), Cotahuasi (dry season only).

Hostelworld barely lists the small hubs (Teresópolis, Potrerillos, San Gerardo, Gracias, Somoto all 0), so use Booking or the guesthouses' own sites there.
