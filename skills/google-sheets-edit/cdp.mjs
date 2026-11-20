#!/usr/bin/env node
// Minimal raw-CDP driver for the persistent Chrome on :9222 (see cdp-up.sh). Needs nothing but
// Node's built-in WebSocket, so it works when the browser MCP servers are disconnected.
//
// CLI:
//   node cdp.mjs list
//   node cdp.mjs open  <url>                      # new tab, prints its id
//   node cdp.mjs nav   <tab> <url>
//   node cdp.mjs eval  <tab> <file.js | src | -> [arg]   # `async (arg) => {...}`; prints JSON
//   node cdp.mjs type  <tab> <text | ->           # real key events; "\n" presses Enter
//   node cdp.mjs key   <tab> Enter|Escape|Tab|Delete|<combo>   # combo e.g. Meta+Alt+Shift+1
//   node cdp.mjs shot  <tab> <out.png>
//   node cdp.mjs cell  <tab> <Sheet!A1>           # Google Sheets: select + read formula bar
//
// <tab> is a target-id prefix or any substring of the tab's URL.
//
// Module: `import { attach, tabs, open } from './cdp.mjs'` — see the exports below.
//
// Never calls Runtime.enable: on Kasada-protected sites that alone gets the tab blocked
// (see SKILL.md). Runtime.evaluate works without it.
import fs from 'node:fs';

const PORT = process.env.CDP_PORT || 9222;
const HTTP = `http://127.0.0.1:${PORT}`;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export const tabs = async () =>
  (await (await fetch(`${HTTP}/json/list`)).json()).filter((t) => t.type === 'page');

export async function findTab(sel) {
  const pages = await tabs();
  return pages.find((p) => p.id.startsWith(sel)) || pages.find((p) => p.url.includes(sel));
}

export async function open(url) {
  const r = await fetch(`${HTTP}/json/new?${encodeURI(url)}`, { method: 'PUT' });
  return (await r.json()).id;
}

const KEYS = {
  Enter: { key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13, text: '\r' },
  Escape: { key: 'Escape', code: 'Escape', windowsVirtualKeyCode: 27 },
  Tab: { key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 },
  Delete: { key: 'Delete', code: 'Delete', windowsVirtualKeyCode: 46 },
};

// Google Sheets: put a range in the name box and return what the formula bar then shows.
// ALWAYS prefix the sheet (`Weeks!B746`) — the name box is relative to the active tab.
const SELECT = `async (ref) => {
  const nb = document.querySelector('#t-name-box');
  nb.focus(); nb.select();
  document.execCommand('insertText', false, ref);
  nb.dispatchEvent(new KeyboardEvent('keydown', {key:'Enter', keyCode:13, bubbles:true}));
  await new Promise(r => setTimeout(r, 700));
  return document.querySelector('#t-formula-bar-input').innerText.trim();
}`;

/** Connect to the tab matching `sel`. Returns helpers bound to that tab. */
export async function attach(sel) {
  const t = await findTab(sel);
  if (!t) throw new Error(`no tab matches "${sel}"`);
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  let id = 0; const pending = new Map();
  ws.onmessage = (e) => {
    const m = JSON.parse(e.data);
    if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  };
  await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
  const send = (method, params = {}) => new Promise((res, rej) => {
    const i = ++id;
    pending.set(i, (m) => (m.error ? rej(new Error(`${method}: ${m.error.message}`)) : res(m.result)));
    ws.send(JSON.stringify({ id: i, method, params }));
  });
  const press = async (k) => {
    await send('Input.dispatchKeyEvent', { type: 'keyDown', ...k });
    await send('Input.dispatchKeyEvent', { type: 'keyUp', ...k, text: undefined });
  };

  const api = {
    target: t,
    send,
    close: () => ws.close(),
    nav: (url) => send('Page.navigate', { url }),
    /** Run `fnSrc` (an `async (arg) => …` source string) in the page; returns its value. */
    async eval(fnSrc, arg) {
      const r = await send('Runtime.evaluate', {
        expression: `(${fnSrc})(${arg === undefined ? 'undefined' : JSON.stringify(arg)})`,
        awaitPromise: true, returnByValue: true, userGesture: true,
      });
      if (r.exceptionDetails) {
        throw new Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
      }
      return r.result.value;
    },
    /** Real keystrokes into whatever has focus. "\n" is Enter. */
    async type(text) {
      await send('Page.bringToFront');
      for (const ch of text) {
        if (ch === '\n') await press(KEYS.Enter);
        else await press({ key: ch, text: ch, unmodifiedText: ch });
        await sleep(15);
      }
    },
    /** Paste plain text (TSV pastes as a grid) into the current selection in ONE action.
     *  Much safer than `type` when the browser is shared: a 28-cell block is one event, not
     *  ~200 keystrokes that another tab can steal focus from. Uses the paste *editing command*,
     *  which is what makes Sheets accept it (a bare Meta+V key event is ignored). Never use it
     *  on dropdown cells — a paste replaces the data validation. */
    async paste(text) {
      await send('Page.bringToFront');
      await send('Browser.grantPermissions', { permissions: ['clipboardReadWrite', 'clipboardSanitizedWrite'],
        origin: new URL(t.url).origin }).catch(() => {});
      await api.eval('async (s) => { window.focus(); await navigator.clipboard.writeText(s); }', text);
      const k = { key: 'v', code: 'KeyV', windowsVirtualKeyCode: 86, modifiers: 4 };
      await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', ...k, commands: ['paste'] });
      await send('Input.dispatchKeyEvent', { type: 'keyUp', ...k });
    },
    /** A named key, or a combo like "Meta+Alt+Shift+1". */
    async key(name) {
      await send('Page.bringToFront');
      if (KEYS[name]) return press(KEYS[name]);
      // `modifiers` is a bitmask (Alt 1, Ctrl 2, Meta 4, Shift 8); the held modifiers are
      // expressed through the mask alone, only the final key is pressed.
      const parts = name.split('+'); const last = parts.pop();
      const modifiers = parts.reduce((m, p) => m | { Alt: 1, Ctrl: 2, Meta: 4, Shift: 8 }[p], 0);
      const code = /^[0-9]$/.test(last) ? `Digit${last}` : `Key${last.toUpperCase()}`;
      const k = { key: last, code, windowsVirtualKeyCode: last.toUpperCase().charCodeAt(0), modifiers };
      await send('Input.dispatchKeyEvent', { type: 'rawKeyDown', ...k });
      await send('Input.dispatchKeyEvent', { type: 'keyUp', ...k });
    },
    async shot(path) {
      const r = await send('Page.captureScreenshot', { format: 'png' });
      fs.writeFileSync(path, Buffer.from(r.data, 'base64'));
      return path;
    },
    /** Sheets: select a cell/range via the name box; returns the formula-bar text. */
    cell: (ref) => api.eval(SELECT, ref),
  };
  return api;
}

// ------------------------------------------------------------------------------ CLI ----
if (import.meta.main) {
  const [cmd, ...args] = process.argv.slice(2);
  const read = (x) => (x === '-' ? fs.readFileSync(0, 'utf8') : x);
  if (cmd === 'list') {
    for (const p of await tabs()) console.log(p.id.slice(0, 8), p.url.slice(0, 110));
  } else if (cmd === 'open') {
    console.log((await open(args[0])).slice(0, 8));
  } else {
    const tab = await attach(args[0]);
    try {
      if (cmd === 'nav') await tab.nav(args[1]);
      else if (cmd === 'eval') {
        const src = read(args[1]);
        const fn = fs.existsSync(src) ? fs.readFileSync(src, 'utf8') : src;
        console.log(JSON.stringify(await tab.eval(fn, args[2]), null, 1));
      } else if (cmd === 'type') await tab.type(read(args[1]));
      else if (cmd === 'key') await tab.key(args[1]);
      else if (cmd === 'shot') console.log(await tab.shot(args[1]));
      else if (cmd === 'cell') console.log(await tab.cell(args[1]));
      else throw new Error(`unknown command ${cmd}`);
    } catch (e) {
      console.error(e.message); process.exitCode = 1;
    } finally { tab.close(); }
  }
}
