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
