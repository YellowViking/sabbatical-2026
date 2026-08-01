/**
 * Google Maps Saved places — batch helper
 * Run inside a logged-in https://www.google.com/maps tab (DevTools console or MCP evaluate).
 *
 * Usage:
 *   1) const template = await MapsSaved.harvestTemplate()  // clicks Save → Want to go (default) on current place
 *   2) const places = await Promise.all(queries.map(MapsSaved.resolvePlace))
 *   3) await MapsSaved.batchSave(template, places)
 */
(function (global) {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  function parseFeature(hexPair) {
    const m = String(hexPair).match(/0x([0-9a-fA-F]+):0x([0-9a-fA-F]+)/i);
    if (!m) return null;
    return {
      hex1: m[1],
      hex2: m[2],
      y1: BigInt("0x" + m[1]).toString(10),
      y2: BigInt("0x" + m[2]).toString(10),
    };
  }

  function buildCreateItemUrl(templateUrl, { lat, lng, y1, y2, name, listId }) {
    let url = templateUrl;
    if (listId) url = url.replace(/(!1m8!1s)[^!]+/, `$1${listId}`);
    url = url.replace(/!3d-?\d+(?:\.\d+)?!4d-?\d+(?:\.\d+)?/, `!3d${lat}!4d${lng}`);
    url = url.replace(/!1y\d+!2y\d+/g, `!1y${y1}!2y${y2}`);
    url = url.replace(
      /!3s[^!]+!9m5/,
      `!3s${encodeURIComponent(name).replace(/%20/g, "+")}!9m5`
    );
    return url;
  }

  async function resolvePlace(query) {
    const url =
      "https://www.google.com/s?tbm=map&gs_ri=maps&suggest=p&authuser=0&hl=en&gl=us&q=" +
      encodeURIComponent(query);
    const t = await (await fetch(url, { credentials: "include" })).text();
    const feat = t.match(/0x[0-9a-fA-F]+:0x[0-9a-fA-F]+/);
    const coord = t.match(/\[null,null,(-?\d+\.\d+),(-?\d+\.\d+)\]/);
    if (!feat || !coord) {
      return { query, error: "unresolved", head: t.slice(0, 200) };
    }
    const f = parseFeature(feat[0]);
    return {
      query,
      name: query,
      lat: parseFloat(coord[1]),
      lng: parseFloat(coord[2]),
      ...f,
    };
  }

  async function harvestTemplate(listMatch = /Want to go/i) {
    const captured = [];
    const xo = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function (m, u, ...r) {
      if (String(u).includes("entitylist/createitem")) captured.push(String(u));
      return xo.call(this, m, u, ...r);
    };
    try {
      const saveBtn = Array.from(document.querySelectorAll("button")).find((b) => {
        const a = (b.getAttribute("aria-label") || "").trim();
        return a === "Save" || a === "Saved";
      });
      if (!saveBtn) throw new Error("No Save button — open a place card first");
      saveBtn.click();
      await sleep(1000);
      const menu = document.querySelector('[aria-label="Save in your lists"]');
      const item =
        menu &&
        Array.from(menu.querySelectorAll('[role="menuitemradio"]')).find((el) =>
          listMatch.test(el.innerText || "")
        );
      if (!item) throw new Error("Target list not found in Save menu");
      // If already checked, still ok — may not re-fire; uncheck/recheck if needed
      item.click();
      await sleep(1200);
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      if (!captured.length) throw new Error("No createitem URL captured");
      return captured[captured.length - 1];
    } finally {
      XMLHttpRequest.prototype.open = xo;
    }
  }

  async function savePlace(templateUrl, place) {
    const url = buildCreateItemUrl(templateUrl, place);
    const res = await fetch(url, {
      credentials: "include",
      headers: { accept: "*/*", "x-same-domain": "1" },
    });
    const text = await res.text();
    return {
      name: place.name || place.query,
      status: res.status,
      ok: res.status === 200 && text.includes(")]}'"),
      resp: text.slice(0, 80),
    };
  }

  async function batchSave(templateUrl, places, delayMs = 60) {
    const results = [];
    for (const p of places) {
      if (p.error) {
        results.push(p);
        continue;
      }
      results.push(await savePlace(templateUrl, p));
      await sleep(delayMs);
    }
    return results;
  }

  global.MapsSaved = {
    parseFeature,
    buildCreateItemUrl,
    resolvePlace,
    harvestTemplate,
    savePlace,
    batchSave,
  };
})(typeof window !== "undefined" ? window : globalThis);
