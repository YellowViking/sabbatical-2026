// IDS='["encarnacion",…]' DIR=/tmp/stop-maps OUT=trips/latam/guides/img node ~/.local/share/cdp-tools/pw.mjs tools/route-map/stop_map_shot.mjs
// Screenshots each <DIR>/<id>.html (from stop_map.py) to <OUT>/<id>-map.jpg once its tiles have loaded.
// Then rename to <id>-map-<sha8>.jpg before committing: GitHub's raw/camo cache keeps serving an old image under the same name for a while.
export default async (page) => {
  const ids = JSON.parse(process.env.IDS); const out = [];
  for (const id of ids) {
    await page.setViewportSize({ width: 1300, height: 900 });
    await page.goto(`file://${process.env.DIR}/${id}.html`, { waitUntil: 'load' });
    await page.waitForFunction(() => [...document.images].every(i => i.complete), null, { timeout: 30000 }).catch(() => {});
    await page.waitForTimeout(+(process.env.WAIT || 500));
    await page.locator('#map').screenshot({ path: `${process.env.OUT}/${id}-map.jpg`, type: 'jpeg', quality: 82 });
    out.push(id);
  }
  return out;
};
