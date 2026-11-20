#!/usr/bin/env node
// Probe the CDP browser on :9222 and report bot-relevant fingerprint surface.
// Usage:  node cdp-check.mjs [host-substring]
//
// Answers two questions without opening a UI:
//   1. Is this browser a real Chrome (vs. an instrumented/headless one)?
//   2. Do we already hold a session for the site I care about?

const PORT = process.env.CDP_PORT || 9222;
const HOST = process.argv[2] || 'hyatt.com';

const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json();
const page = list.find((t) => t.type === 'page' && t.url.includes(HOST)) ||
             list.find((t) => t.type === 'page' && !t.url.startsWith('chrome'));

if (!page) {
  console.log('No usable page target. Open a tab first, or pass a host substring.');
  process.exit(0);
}

const ws = new WebSocket(page.webSocketDebuggerUrl);
let id = 0;
const pending = new Map();
const send = (method, params = {}) =>
  new Promise((res) => { const i = ++id; pending.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m.result); pending.delete(m.id); }
};
await new Promise((r) => { ws.onopen = r; });

const probe = await send('Runtime.evaluate', {
  expression: `JSON.stringify({
    url: location.href,
    webdriver: navigator.webdriver,
    hasChromeObject: !!window.chrome,
    hasRuntime: !!(window.chrome && window.chrome.runtime),
    plugins: navigator.plugins.length,
    mimeTypes: navigator.mimeTypes.length,
    languages: navigator.languages,
    platform: navigator.platform,
    userAgent: navigator.userAgent,
    hardwareConcurrency: navigator.hardwareConcurrency,
    deviceMemory: navigator.deviceMemory ?? null
  })`,
  returnByValue: true,
});

const fp = JSON.parse(probe.result.value);
const cookies = (await send('Network.getAllCookies')).cookies || [];
const forHost = cookies.filter((c) => c.domain.includes(HOST));

const verdict = [];
if (fp.webdriver) verdict.push('navigator.webdriver=TRUE  <-- automation leak');
if (!fp.hasChromeObject) verdict.push('window.chrome missing  <-- automation leak');
if (!fp.hasRuntime) verdict.push('chrome.runtime missing  <-- CDP-attach tell');
if (/Headless|Chromium/.test(fp.userAgent)) verdict.push('UA looks headless/virtual  <-- leak');
if (fp.plugins === 0) verdict.push('zero plugins  <-- leak');
if (fp.mimeTypes === 0) verdict.push('zero mimeTypes  <-- leak');

console.log(`target : ${fp.url}`);
console.log(`browser: ${fp.userAgent.match(/Chrome\/[\d.]+/)?.[0] ?? 'n/a'} | platform ${fp.platform} | cores ${fp.hardwareConcurrency}`);
console.log(`surface: webdriver=${fp.webdriver} chrome=${fp.hasChromeObject} runtime=${fp.hasRuntime} plugins=${fp.plugins} mimeTypes=${fp.mimeTypes}`);
console.log(`verdict: ${verdict.length ? verdict.join('; ') : 'looks like a real Chrome ✅'}`);
console.log(`${HOST} cookies: ${forHost.length}`);
if (forHost.length) {
  console.log('  ' + forHost.map((c) => c.name).sort().join(', '));
  const sessiony = forHost.filter((c) => /session|SID|auth|token|_csrf|at_check|abck/i.test(c.name));
  console.log(`  session-ish: ${sessiony.length ? sessiony.map((c) => c.name).join(', ') : 'none — log in once in this window'}`);
}
process.exit(0);