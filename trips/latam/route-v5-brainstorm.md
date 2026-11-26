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

**Rechecked 25 Nov against Lonely Planet Central America (2025) and Lonely Planet Brazil:**
- **Lonely Planet Central America:**
  - Costa Rica's dry season is December–April, with December only its start. Its Guanacaste chart shows rain on 13 days in December, 7 in January, 4 in February and 3 in March.
  - Panama's dry season is also its peak, with the best birding in February–April.
  - Nicaragua's dry season is November–April, and January has some of its best weather.
  - Prices spike at Christmas and Easter.
- **Lonely Planet Brazil:**
  - High season is December–March.
  - February means packed beaches, sold-out hotels and Carnaval prices.
  - Prices and heat ease only from April.
- **Rio station normals** give a small edge to late February: ≈ 8–9 rain days a month in February–March, against ≈ 11 in December.
- **Re-scored with the actual v5 dates:**

| Order | Wet days | Peak-season days |
|---|---:|---:|
| **v5 as planned** (South America first) | **37.4** | **12** |
| Reversed (Central America 8 Dec – 5 Jan, Brazil 22 Feb – 3 Mar) | 42.8 | 27 (Costa Rica over Christmas and New Year) |
| Andes first (Andes in Dec, Brazil late Jan, Central America in Feb) | 36.0 | 25 (Uruguay and Córdoba in January, Brazil before Carnaval) |

The v5 order stays.

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

**Award sweep, extended (24 Nov, award only):**
- **Alaska, more dates:** Wed 9 Dec has the same PHL route as 7 Dec (AA771 → AA688 787 lie-flat first → AA905), 2 seats. Thu 10 Dec: SEA–CLT → AA574 777 lie-flat first → AA991, 2 seats. Both 60k + $26.
- **Alaska to São Paulo (GRU), 60k + $26:**
  - Tue 8 Dec: SEA–ORD–MIA in first → **AA929 777-300ER** business, 19 h, 3 seats.
  - Wed 2 / Thu 3 Dec: via CLT (777 first) → AA929 / AA995, 1 seat each.
  - Mon 7 Dec: red-eye SEA–MIA in first → AA929, 8 seats, but 14 h in Miami.
  - Nothing on 4–6 Dec. GRU would mean starting the corridor in São Paulo, or a cash hop GRU → GIG.
- **Delta (SkyMiles):** Delta One SEA → GRU is **482,500–499,900 miles** for every date 4–10 Dec, so not worth it. Partners (Virgin, Flying Blue) only get Delta's saver space, so they're out too.
- **United / Star Alliance (Chase → United; also what Aeroplan and LifeMiles see):**
  - No Polaris saver to GIG or GRU; Standard costs 295–395k.
  - No Air Canada saver YYZ → GRU appeared.
  - The only saver "business" is Avianca A320 recliners via Bogotá at 88k.
  - Aeroplan sometimes has extra Air Canada space that partners don't see. Worth checking only with an Aeroplan sign-in.

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

## 11. Panama kept (user, 24 Nov)

Panama becomes the way into Central America, so the north-west run never doubles back:

| Leg | Notes |
|---|---|
| ✈ Arequipa → Lima $62, then ✈ Lima → Panama City $254 | Google Flights doesn't sell these as one ticket (it showed $1,400+ via Mexico). Book two tickets and leave a long gap or a night in Lima. Arequipa → San José was $263, so Panama costs ≈ $53 more |
| Panama City (2 nights) | Casco Viejo, the Canal, Parque Natural Metropolitano |
| → Boquete (3–4 nights), via a ~7 h bus to David or a short flight | **Adventure hub:** Volcán Barú 3,474 m sunrise climb, Lost Waterfalls, the Quetzal trail, Chiriquí rafting. February is the dry season (rain on 22% of days in Panama) |
| → Paso Canoas border → San Isidro → **San Gerardo de Rivas (Chirripó)** | Costa Rica starts at its southern end |
| → Uvita / Dominical → Manuel Antonio → Monteverde → Arenal → Rincón de la Vieja → Nicaragua (south → north) | Mountains, then coast, then cloud forest, then volcanoes |

**Days:** with Panama the route is 91 typical days.
- Land in Rio **8 Dec** (business 7 Dec): ends ≈ **11 Mar**, leaving only **4 days** before 15 Mar.
- Land in Rio **4 Dec** (business 3 Dec, 1 seat; or economy 30k on 2 or 4 Dec, 9 seats): ends ≈ 7 Mar, leaving 8 days.
- The adventure-hub extras from section 10 (≈ +6 days) don't fit without cutting from the end. The candidate is Nicaragua (14 days), e.g. Somoto plus one beach night, ≈ −4.

## 12. Every leg: how, how long, how much (24 Nov)

✅ = checked live today (Google Flights price calendar, Alaska award search, the v4 itinerary's live checks). ≈ = Google AI Mode summaries of Busbud, CheckMyBus, Rome2Rio and operator sites. Confirm ≈ prices on the operator's own shop when booking.

| # | Leg | How | Time | Cost (USD) |
|---|---|---|---|---|
| 1 | Seattle → Rio (GIG) | ✈ AA via Philadelphia + Miami, Alaska award, business with first-class US legs | 19 h | ✅ 60k pts + $26 (economy 30k + $26) |
| 2 | GIG → Copacabana | BRT + metro (or Uber) | ~1 h | ✅ $2 (Uber $10–17) |
| 3 | Rio → Ilha Grande | Bus to Conceição de Jacareí + boat (or Angra + state ferry) | 3–3½ h | ≈ $17–25 |
| 4 | Ilha Grande → Paraty | Ferry 10:00 + Colitur bus 12:40 | ~3½ h | ✅ $9 (R$48) |
| 5 | Paraty → São Paulo | Reunidas bus | 6½–7 h | ✅ $19 (R$100) |
| 6 | São Paulo → Curitiba | Bus (Cometa, Penha, FlixBus) | 6½–7½ h | ≈ $16–26 |
| – | *optional:* Curitiba → Morretes → Curitiba | Serra Verde Express train 08:30 (4 h), bus back (1¼ h) | day trip | ≈ $38–40 + $6–9 |
| 7 | Curitiba → Foz do Iguaçu | Overnight bus, semi-sleeper (sleeper $80–100; flight $95–180) | 10–12 h | ≈ $53–67 |
| 8 | Foz → Ciudad del Este → Asunción | Border bus + NSA/RYSA bus | 5½–7 h | ≈ $14–22 |
| 9 | Asunción → Encarnación | Bus (NSA) | 5–6 h | ≈ $10–27 |
| 10 | Encarnación → Posadas | International train over the bridge | 8 min | ≈ $2–4 |
| 11 | Posadas → Concordia | Overnight bus (Crucero del Norte, Flechabus) | 8–9½ h | ≈ $26–57 |
| 12 | Concordia → Salto | Bus over the dam (11:15 or 18:15) | ~1 h | ≈ $6–7 |
| 13 | Salto → Montevideo | Bus (Agencia Central) | 6–6½ h | ≈ $35–45 |
| 14 | Montevideo → Cabo Polonio | Rutas del Sol bus + 4x4 truck into the village (truck sold as a round trip; park included) | ~5 h | ≈ $25 + $11.50 |
| 15 | Cabo Polonio → Colonia | Bus via Montevideo (the spur back) | 8–8½ h | ≈ $39–42 |
| 16 | Colonia → Buenos Aires | Ferry (Colonia Express cheaper than Buquebus) | 1¼ h | ≈ $42–67 |
| 17 | Buenos Aires → Córdoba | Overnight bus, sleeper | 8–9½ h | ≈ $45–65 |
| 18 | Córdoba → Mendoza | Overnight bus (semi-sleeper; sleeper $60–85) | 9–10½ h | ≈ $25–45 |
| 19 | Mendoza → Santiago | Day bus over the Andes (take the 7–8 am bus) | 7–9 h | ≈ $25–48 |
| 20 | Santiago → Calama | ✈ JetSMART / Sky / LATAM | 2 h | ✅ $43–88 ($43 on 6–10 Jan) |
| 21 | Calama → San Pedro de Atacama | Bus | 1½ h | ≈ $7–17 |
| 22 | San Pedro → Salta | Andesmar 07:30 over Paso de Jama (~6 days a week) | 10½–11½ h | ≈ $65–98 |
| 23 | Salta → Jujuy → Purmamarca / Tilcara / Humahuaca | Buses along Ruta 9 | 1½–2½ h + 1–2½ h | ≈ $13–30 |
| 24 | Humahuaca → La Quiaca, walk the border | Bus | 2–3 h | ≈ $9–14 |
| 25 | Villazón → Tupiza | Bus | 1½–2 h | ≈ $4–8 |
| 26 | Tupiza → Uyuni | **4-day jeep tour** (lodging and food included) + park fees | 4 days | ≈ $220–400 + $50–100 |
| 27 | Uyuni → Potosí | Bus | 4 h | ≈ $6–18 |
| 28 | Potosí → Sucre | Bus or shared taxi | 2½–4 h | ≈ $6–12 |
| 29 | Sucre → La Paz | ✈ BoA, daily | 50 min | ✅ $50 |
| 30 | La Paz → Copacabana | Bus + the Tiquina boat | 3½–4½ h | ≈ $4–9 |
| 31 | Copacabana → Puno | Bus, Kasani border included | 3½–4½ h | ≈ $7–17 |
| 32 | Puno → Chivay (Colca) | 4M Express tourist bus (Rutas del Sur $35–40) | ~6¼ h | ≈ $50–54 |
| 33 | Chivay → Cabanaconde | Local bus (passes Cruz del Cóndor) | 1½–2½ h | ≈ $3–5 |
| 34 | Cabanaconde → Arequipa | Bus | 5½–6½ h | ≈ $10–14 |
| 35 | Arequipa → Lima → Panama City | ✈ two tickets (Sky/LATAM, then Copa) | 1½ h + 3½ h + layover | ✅ $62 + $254 |
| 36 | Panama City → David → Boquete | Bus from Albrook (flight $70–190) + local bus | 7½–8½ h | ≈ $17–28 |
| 37 | Boquete → David → Paso Canoas | 2 buses | ~2½ h | ≈ $5–15 |
| 38 | Paso Canoas → San Isidro → San Gerardo de Rivas | Tracopa (Interamericana route) + local bus | 5½–7 h | ≈ $13–24 |
| 39 | San Gerardo → San Isidro → Uvita | 2 buses | ~2½ h | ≈ $6–10 |
| 40 | Uvita → Quepos / Manuel Antonio | Bus | 1¾–2½ h | ≈ $5–12 |
| 41 | Quepos → Monteverde | 2 buses via Puntarenas | 5½–6½ h | ≈ $10–15 |
| 42 | Monteverde → La Fortuna | Jeep-boat-jeep | 3–4 h | ≈ $30–40 |
| 43 | La Fortuna → Liberia (Rincón de la Vieja) | 3 buses via Tilarán and Cañas (shuttle ~3 h) | 3½–4½ h | ≈ $7–15 |
| 44 | Liberia → Peñas Blancas → San Juan del Sur | Bus + Nicaraguan buses via La Virgen | 3½–4 h | ≈ $5–8 + **Costa Rica exit $8–9 + Nicaragua entry $14** (cash) |
| 45 | San Juan del Sur → Ometepe | Bus to Rivas + colectivo + ferry from San Jorge | ~2½ h | ≈ $4–7 |
| 46 | Ometepe → Granada | Ferry + buses via Rivas | 3½–4½ h | ≈ $4–6 |
| 47 | Granada → León | 2 microbuses via Managua (shuttle $25–36) | 2½–3 h | ≈ $3 |
| – | *optional:* León → Estelí → Somoto | Buses | 3½–5 h | ≈ $4–5 |
| 48 | León → Managua airport | Bus (shuttle $25–35) | 1½–2 h | ≈ $3 |
| 49 | Managua → Seattle | ✈ AA via Miami | 14–17 h | ✅ 25k pts + $94, or $417 cash (business 50k is first only to Miami) |

**Totals:** ground transport, the Calama, La Paz and Panama flights, and border fees come to ≈ **$1,150–1,590**. The Uyuni jeep tour adds $270–500, but it also covers 4 nights' lodging and food. Points: 60k (in, business) + 25k (home, economy).

**Adventure-hub legs (if added):**
- GIG → Teresópolis, bus 2 h ≈ $10, then Teresópolis → Rio 2 h ≈ $10.
- Mendoza → Potrerillos, 1¼ h ≈ $5–7.
- Santiago ↔ Baños Morales (El Morado), Metrobús 72A 2–2½ h ≈ $5 each way.
- Cerro Toco, guided tour ≈ $110–150.

## 13. Two questions (24 Nov): Buquebus direct? Do we need Santiago?

**Montevideo → Buenos Aires.** We come back through Montevideo from Cabo Polonio anyway.

| Option | Time | Late-Dec fare | Notes |
|---|---|---|---|
| Buquebus direct, Montevideo port → Puerto Madero | 2 h 45 | ≈ $100–180 (peak pricing) | Sails ≈ 11:00 and 19:30. One immigration stop, at the Montevideo port. Skips Colonia |
| Bus to Colonia (≈ 2 h 45, ≈ $15) + **4–5 h in Colonia's old town** (luggage storage at the terminal) + Colonia Express ferry (1 h 15) | a full travel day | ≈ $55–80 | Colonia's UNESCO old town is free to walk. Buy bus and ferry separately, because through-tickets allow only 30–45 min to change |

Recommendation: the **Colonia stopover**. It's ≈ $50–100 cheaper and includes the sight. Ferries are reduced on 24, 25 and 31 Dec (last Colonia sailing ≈ 16:15).

**Santiago is optional.** The no-Santiago route runs in a straight line from Córdoba to La Paz with no flight:

| Leg | How | Time | USD (≈) |
|---|---|---|---|
| Córdoba → Tucumán | Overnight bus (22:50 / 23:45) | ≈ 8½ h | $19–57 |
| Tucumán → Cafayate | Aconquija bus via Tafí del Valle (06:00, 10:00, 14:00) | 6–6½ h | $23–27 |
| Cafayate → Salta | Flecha Bus through Quebrada de las Conchas (sit on the left) | 3½–4 h | $17–25 |
| Salta → Jujuy → Purmamarca / Tilcara | Buses | 2½–4 h | $13–20 |
| Purmamarca → San Pedro de Atacama | Andesmar over Paso de Jama, **03:40** (Jujuy 02:45), arrives ≈ 11:30 | ≈ 8 h | $70–97 |
| San Pedro → Uyuni | 3-day jeep tour | 3 days | $240–290 + fees |
| Uyuni → Potosí → Sucre → ✈ La Paz | as before | | |

**Gains:**
- 5 days back: the trip ends ≈ 6 Mar with 9 spare days, against 4 with Santiago.
- No Santiago → Calama flight, no Mendoza or Cristo Redentor buses.
- Cafayate and Salta are on the line instead of spurs.

**Loses:**
- Santiago and Valparaíso.
- **Cajón del Maipo** (El Morado, in prime season).
- The Cristo Redentor crossing, though Jama at 4,200 m replaces it.
- Tupiza's quieter 4-day tour. San Pedro's 3-day tour climbs fast, so spend the San Pedro days first to acclimatise.

Chile is still visited (San Pedro). Tafí del Valle is very wet in summer (rain on ~80% of days, fog), so ride through it.

Model with Panama, landing 8 Dec: −1.0 with Santiago vs −2.9 without. The model counts Santiago as dry, new-country days.

## 14. How other travellers route it (web sweep, 24 Nov)

Sources:
- Google AI Mode summaries of r/backpacking, r/solotravel, r/SouthAmericaTravel and blogs (Worldly Adventurer, The Broke Backpacker, Bolivian Life).
- A few Reddit threads read directly via Reddit's JSON in the browser. They were thin, with few comments.
- LP Brazil's itineraries chapter.

| Section | What most people do | Ours | Verdict |
|---|---|---|---|
| Brazil | Rio → Ilha Grande / Paraty (6–8 days) → São Paulo → Curitiba (+ Serra Verde train) → Iguaçu, by overnight bus or flight | Same | ✔ |
| Paraguay → Uruguay | **Iguazú → Asunción → Encarnación → Posadas → Concordia → Salto → Montevideo → Colonia → Buenos Aires**. This corridor avoids passing Buenos Aires twice. Keep Paraguay short (1–2 nights each in Asunción and Encarnación). Colonia is a 3–4 h stopover with bags left at the terminal | Same | ✔ an exact match |
| Argentina → Atacama → Uyuni | Most people heading north go **Salta → Paso de Jama → San Pedro (2+ nights to acclimatise) → 3-day tour → Uyuni**, "zero backtracking". Tupiza's 4-day tour is better for altitude and crowds, but people usually take it heading *south* into Chile. Santiago is treated as a ≤ 48 h hub | With Santiago: San Pedro → Salta → Tupiza → Uyuni. San Pedro's lagoons then repeat on the Tupiza tour | **Prefer the no-Santiago line** (§13): Córdoba → Cafayate → Salta → Jujuy → Jama → San Pedro → Uyuni. It's the standard northbound route |
| Bolivia → Peru | Uyuni (3) → Potosí (1 night, mine tour) → Sucre (2–3) → **fly** to La Paz → La Paz (2–3) → Copacabana / Isla del Sol (**1–2 nights**) → Puno only as a transit stop → **get off at Chivay** → Colca trek → Arequipa | Same, but Titicaca has 3 days | Trim Titicaca to 2 nights (−1 day) |
| Exit to Central America | Fly from Lima | Arequipa → Lima → Panama City | ✔ |
| Panama → Costa Rica → Nicaragua | Panama City (2–3) → Boquete (3–4) → (Bocas → Sixaola if you want the Caribbean) or **Paso Canoas** → San Gerardo / Chirripó (3–4) → Uvita (2–3) → Monteverde (2–3) → jeep-boat-jeep → La Fortuna (3) → Peñas Blancas | Same, Paso Canoas | ✔ (Bocas skipped: it's a beach) |

**Warnings that apply to us:**
- **Pace.** Reddit's top regret is too many countries in about 90 days; people say they'd cut 2–3. We have 10 countries in ≈ 95 days. Overnight buses help. Avoid consecutive 15–24 h rides, and keep one-night stops rare.
- **Rain in the Andes.** Some advise pushing Bolivia and Peru into March. The station data agree March is drier than January (Copacabana: rain on 43% of days vs 63%). But that would mean flying back from Central America to the Andes, which is backtracking, so we keep January. The rains do bring Uyuni's **mirror season** (Jan–Mar), though a flooded salt flat can block Isla Incahuasi.
- **Commonly cut:** Asunción, long stays in Puno, Santiago and Lima beyond 48 h, and Uruguay on a tight budget. We keep Uruguay to tick off the country.

## 15. Route v5, locked skeleton (user, 24 Nov: Santiago dropped, Panama kept)

> **Refined in the [itinerary](itinerary.md) (24 Nov, after live checks).** The changes:
> - Córdoba city + Los Gigantes refugio replace a Sierras town.
> - The Quebrada is split Tilcara 1 + Purmamarca 1.
> - Colca is split Chivay 1 + Sangalle oasis 1.
> - Encarnación → Montevideo is EGA (Wed/Sat).
> - Sierra de las Ánimas is dropped (weekends only, no luggage storage).
> - Boquete is reached by Air Panama.
> - Chirripó climb on 10 → 11 Feb.
> - León gets 3 nights + a Managua airport night.
>
> The table below is the pre-check skeleton.

Decisions so far:
- Brazil is cut to the Rio–São Paulo corridor; no Bahia.
- Paraguay and Uruguay go via the standard corridor.
- **No Santiago.**
- Córdoba replaces Mendoza.
- The northbound line is Salta → Jama → San Pedro → Uyuni.
- Titicaca gets 2 nights.
- Panama is the entry to Central America.
- Honduras is out.

Dates assume the **Alaska business award on Mon 7 Dec** (lands Rio Tue 8 Dec 09:25). Stays are typical-length (consensus) days only. **Adventure extras (Teresópolis +2, Cerro Toco and Pico Austria inside San Pedro and La Paz) are not yet in the table.** Nothing is booked.

| # | Stop | Dates | Nights | Scenery | Note |
|---|---|---|---|---|---|
| 1 | Rio de Janeiro | Tue 8 Dec → Sat 12 Dec | 4 | city + peaks | Tijuca, Pedra da Gávea, beaches |
| 2 | Ilha Grande | Sat 12 Dec → Mon 14 Dec | 2 | island jungle + beach | Pico do Papagaio, Lopes Mendes |
| 3 | Paraty | Mon 14 Dec → Tue 15 Dec | 1 | colonial + waterfalls |  |
| 4 | São Paulo | Tue 15 Dec → Thu 17 Dec | 2 | megacity |  |
| 5 | Curitiba | Thu 17 Dec → Fri 18 Dec | 1 | city | Serra Verde train to Morretes next morning, bus back |
|  | overnight bus Curitiba → Foz | Fri 18 Dec → Sat 19 Dec | 1 |  |  |
| 6 | Foz do Iguaçu | Sat 19 Dec → Mon 21 Dec | 2 | waterfalls | Brazilian + Argentine sides |
| 7 | Asunción | Mon 21 Dec → Wed 23 Dec | 2 | city |  |
| 8 | Encarnación | Wed 23 Dec → Sat 26 Dec | 3 | river town, Jesuit ruins | Trinidad/Jesús ruins; Christmas here |
|  | Sat 26 Dec: direct bus Encarnación → Montevideo (Wed/Sat, 14–18 h) | Sat 26 Dec → Sun 27 Dec | 1 |  |  |
| 9 | Montevideo | Sun 27 Dec → Mon 28 Dec | 1 | city |  |
| 10 | Cabo Polonio | Mon 28 Dec → Wed 30 Dec | 2 | dunes + beach | Sierra de las Ánimas on the way |
| 11 | Montevideo (New Year) | Wed 30 Dec → Fri 1 Jan | 2 | city |  |
|  | Colonia 4–5 h stopover → ferry → BA → overnight bus to Córdoba | Fri 1 Jan → Sat 2 Jan | 1 |  |  |
| 12 | Córdoba + Sierras | Sat 2 Jan → Thu 7 Jan | 5 | hills | Condorito (free), Los Gigantes 2-day |
|  | overnight bus Córdoba → Tucumán, then bus to Cafayate | Thu 7 Jan → Fri 8 Jan | 1 |  |  |
| 13 | Cafayate | Fri 8 Jan → Sun 10 Jan | 2 | wine valley, red canyons | Quebrada de las Conchas |
| 14 | Salta | Sun 10 Jan → Tue 12 Jan | 2 | city |  |
| 15 | Purmamarca / Tilcara | Tue 12 Jan → Thu 14 Jan | 2 | coloured canyons | Garganta del Diablo, Hornocal |
| 16 | San Pedro de Atacama | Thu 14 Jan → Mon 18 Jan | 4 | desert | acclimatise; Valle de la Luna by bike; Cerro Toco optional |
| 17 | Uyuni jeep tour | Mon 18 Jan → Wed 20 Jan | 2 | lagoons, geysers, salt flat | 3-day tour, nights in refugios |
| 18 | Potosí | Wed 20 Jan → Thu 21 Jan | 1 | mining city | Cerro Rico mine tour |
| 19 | Sucre | Thu 21 Jan → Sun 24 Jan | 3 | colonial city | Maragua crater hike |
| 20 | La Paz | Sun 24 Jan → Wed 27 Jan | 3 | mountain city | teleférico, Death Road or Pico Austria |
| 21 | Copacabana + Isla del Sol | Wed 27 Jan → Fri 29 Jan | 2 | lake + islands | Isla del Sol N–S ridge walk |
| 22 | Puno | Fri 29 Jan → Sat 30 Jan | 1 | transit | 4M Express leaves ~06:00 |
| 23 | Colca (Chivay / Cabanaconde) | Sat 30 Jan → Mon 1 Feb | 2 | canyon | Cabanaconde → Sangalle, climb out at 5 am |
| 24 | Arequipa | Mon 1 Feb → Wed 3 Feb | 2 | colonial city |  |
| 25 | Panama City | Wed 3 Feb → Fri 5 Feb | 2 | city + canal | ✈ Arequipa → Lima → Panama City |
| 26 | Boquete | Fri 5 Feb → Mon 8 Feb | 3 | cloud forest + volcano | Volcán Barú sunrise, Lost Waterfalls |
| 27 | San Gerardo de Rivas (Chirripó) | Mon 8 Feb → Thu 11 Feb | 3 | high mountain | 2-day Chirripó; SINAC + Crestones booking |
| 28 | Uvita | Thu 11 Feb → Sat 13 Feb | 2 | beach | Marino Ballena, whale tail |
| 29 | Monteverde | Sat 13 Feb → Mon 15 Feb | 2 | cloud forest | Santa Elena reserve |
| 30 | La Fortuna / Arenal | Mon 15 Feb → Thu 18 Feb | 3 | volcano + hot rivers | El Chollín free hot river |
| 31 | Liberia / Rincón de la Vieja | Thu 18 Feb → Sat 20 Feb | 2 | dry forest + volcano |  |
| 32 | San Juan del Sur / Playa Maderas | Sat 20 Feb → Mon 22 Feb | 2 | surf beach |  |
| 33 | Ometepe | Mon 22 Feb → Thu 25 Feb | 3 | lake island volcanoes | Concepción with a guide |
| 34 | Granada + Apoyo | Thu 25 Feb → Sat 27 Feb | 2 | colonial city + crater lake |  |
| 35 | León | Sat 27 Feb → Wed 3 Mar | 4 | colonial city + volcanoes | Cerro Negro, Telica overnight |

**26 Nov update:** Iruya (1 night, taken from San Pedro), a Laguna de Apoyo night (from Granada) and Estelí (+1 day) were added after the article review; the flight home moved to **Thu 4 Mar** (same award), leaving 11 spare days. See the [itinerary](itinerary.md).

**Home: ✈ Managua → Seattle on Wed 3 Mar** (Alaska 25k + $94, or $417 cash). That leaves **12 spare days before 15 Mar**, against the 14-day floating buffer. Options for them:
- Somoto canyon (+2) on the way out.
- Teresópolis (+2).
- Pico Austria (+2).
- Weather or rest days.

**Changed legs vs section 12** (≈ = AI-summary estimates; confirm on the operators' sites):

| Leg | How | Time | USD |
|---|---|---|---|
| Encarnación → Montevideo | Direct bus (EGA / NSA, **Wed & Sat**), avoiding a Christmas-night bus via Concordia | 14–18 h | ≈ $100–155 |
| Montevideo ↔ Cabo Polonio | Rutas del Sol + 4x4 truck (round trip) | ≈ 5 h each way | ≈ $36.50 out, $25 back |
| Montevideo → Colonia → Buenos Aires | Bus (≈ 2 h 45), 4–5 h in the old town, Colonia Express ferry (Buquebus direct ≈ $100–180 is the fast alternative). Ferries are reduced on 31 Dec and 1 Jan, so the crossing may slip to 2 Jan | a day | ≈ $13–17 + $42–67 |
| Buenos Aires → Córdoba | Overnight bus, sleeper | 8–9½ h | ≈ $45–65 |
| Córdoba → Tucumán → Cafayate | Overnight bus, then Aconquija 06:00/10:00 via Tafí del Valle | 8½ h + 6–6½ h | ≈ $19–57 + $23–27 |
| Cafayate → Salta | Flecha Bus through Quebrada de las Conchas | 3½–4 h | ≈ $17–25 |
| Salta → Jujuy → Purmamarca | Buses | ≈ 3 h | ≈ $10–18 |
| Purmamarca → San Pedro de Atacama | Andesmar over Paso de Jama, **03:40** → ≈ 11:30 | ≈ 8 h | ≈ $80–97 |
| San Pedro → Uyuni | 3-day jeep tour (Bolivian park fee, Incahuasi, hot springs extra) | 3 days | ≈ $240–290 + $50–100 |
| Uvita → Monteverde | Buses via Quepos and Puntarenas (Manuel Antonio dropped; Uvita is the Pacific beach stop) | ≈ 7 h | ≈ $12–18 |

The Córdoba → Mendoza → Santiago buses, the Santiago → Calama flight and the Tupiza tour are all gone.

**Transport total:** ground transport, the La Paz and Panama flights and border fees come to ≈ **$1,180–1,550**. The jeep tour adds ≈ $290–390, including park fees, and covers 2 nights' beds. Points: 60k in (business) + 25k home (economy).
