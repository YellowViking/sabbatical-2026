---
name: flights-points-vs-cash
description: "When planning flights/hotels, cross-check points/miles redemption vs. cash before recommending a booking; Google Flights is the cash baseline"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e02c15bb-b0a4-409b-b0b7-f59669d2af3f
---

When planning any flight or hotel, cross-check **points/miles redemption value against the cash price** whenever a redemption could plausibly make sense — don't just quote cash. Use **Google Flights as the cash-price baseline** (user finds it reliable for cash estimates).

**Why:** The user actively optimizes travel with points/miles and doesn't want to overpay cash on a booking where a redemption is clearly better value (or vice-versa — burn miles on a cheap ticket where cash is better).

**How to apply:** Compute cents-per-point = (cash price ÷ points required). Rule of thumb — redeem when value clears ~1.3–1.5¢/pt or higher (premium cabins, expensive routes, pricey hotel nights, one-way flights home); pay **cash** on cheap economy positioning legs where redemption would come in under ~1¢/pt. To do this concretely I need the user's program balances + status (transferable points like Amex MR / Chase UR / Capital One / Bilt, airline miles, hotel points). Link [[sabbatical-2026-europe]].
