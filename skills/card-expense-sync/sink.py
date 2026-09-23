#!/usr/bin/env python3
"""Tiny localhost sink so the Playwright sandbox can persist what it pulls.

The Playwright MCP `browser_run_code_unsafe` sandbox has no `require`/`fs`/`process`,
so a script running there cannot write files. It CAN make HTTP calls. This server
accepts a POST and writes the body to disk, keeping raw bank payloads out of the
agent's context and out of the public git repo.

    python3 sink.py [outdir]     # defaults to ~/Documents/sabbatical-finance/raw
"""
import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

OUTDIR = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
    "~/Documents/sabbatical-finance/raw"
)
PORT = 8899


CONFIG = os.path.join(os.path.dirname(OUTDIR), "accounts.json")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve files the sandbox needs but cannot open from disk (no fs there).

        /config  -> accounts.json      /payload -> payload.json (a paste job for paste.js)
        """
        which = self.path.rstrip("/")
        src = {"/config": CONFIG, "/payload": os.path.join(os.path.dirname(OUTDIR), "payload.json")}.get(which)
        if not src or not os.path.exists(src):
            self.send_error(404)
            return
        with open(src, "rb") as fh:
            body = fh.read()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        # Page-context JS (CDP `evaluate_script`) is subject to CORS, unlike Playwright's
        # request context. Without this a script running inside docs.google.com cannot read
        # the payload and it has to be inlined into the call.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _run_pipeline(self):
        """categorize.py + build_blocks.py, so the browser never leaves its one call."""
        import subprocess

        cfg = json.load(open(CONFIG))
        sheet = cfg.get("sheet", {})
        here = os.path.dirname(os.path.abspath(__file__))
        work = os.path.dirname(OUTDIR)
        steps = [
            # No --end: it is only a filter, and the grid self-terminates at the last day with
            # a figure. Passing today's date would drop prepaid future lodging nights.
            [sys.executable, os.path.join(here, "categorize.py"),
             "--start", sheet.get("startISO", "2026-08-24")],
            [sys.executable, os.path.join(here, "build_blocks.py"),
             "--first-row", str(sheet.get("firstRow", 684)),
             "--sheet-url", sheet.get("url", "")],
        ]
        out = []
        for cmd in steps:
            r = subprocess.run(cmd, cwd=work, capture_output=True, text=True)
            out.append(r.stdout.strip() or r.stderr.strip())
            if r.returncode:
                return {"ok": False, "log": out}
        payload = json.load(open(os.path.join(work, "payload.json")))
        return {"ok": True, "log": out, "payload": payload}

    def do_POST(self):
        if self.path.rstrip("/") == "/process":
            res = self._run_pipeline()
            body = json.dumps(res).encode()
            self.send_response(200 if res["ok"] else 500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            print("ran pipeline:", "; ".join(res["log"])[:300], flush=True)
            return

        # /chase and /amex arrive separately from their own bank tabs (CDP path); stitch them
        # into one sync file so categorize.py sees the same shape as a Playwright pull.
        if self.path.rstrip("/") in ("/chase", "/amex"):
            which = self.path.strip("/")
            data = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))))
            part = os.path.join(OUTDIR, f"_part-{which}.json")
            os.makedirs(OUTDIR, exist_ok=True)
            with open(part, "w") as fh:
                json.dump(data, fh)
            have = {w: os.path.exists(os.path.join(OUTDIR, f"_part-{w}.json"))
                    for w in ("chase", "amex")}
            merged = None
            if all(have.values()):
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                merged = os.path.join(OUTDIR, f"sync-{stamp}.json")
                with open(merged, "w") as fh:
                    json.dump({
                        "pulledAt": datetime.now(timezone.utc).isoformat(),
                        "chase": json.load(open(os.path.join(OUTDIR, "_part-chase.json"))),
                        "amex": json.load(open(os.path.join(OUTDIR, "_part-amex.json"))),
                    }, fh)
                for w in ("chase", "amex"):
                    os.remove(os.path.join(OUTDIR, f"_part-{w}.json"))
            res = json.dumps({"stored": which, "have": have, "merged": merged}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(res)))
            self.end_headers()
            self.wfile.write(res)
            print(f"stored {which}; merged={merged}", flush=True)
            return

        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        name = self.path.strip("/").replace("/", "_") or "payload"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        os.makedirs(OUTDIR, exist_ok=True)
        path = os.path.join(OUTDIR, f"{name}-{stamp}.json")
        with open(path, "wb") as fh:
            fh.write(body)
        print(f"wrote {path} ({len(body)} bytes)", flush=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"wrote": path, "bytes": len(body)}).encode())

    def log_message(self, *_):  # keep stdout to just the writes
        pass


if __name__ == "__main__":
    print(f"sink listening on http://127.0.0.1:{PORT} -> {OUTDIR}", flush=True)
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
