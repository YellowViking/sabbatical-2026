#!/usr/bin/env bash
# Bring up (or reuse) a PERSISTENT Chrome on CDP port 9222 for spreadsheet work.
#
#   bash cdp-up.sh
#
# Idempotent: if something is already answering on 9222, it does nothing and exits 0. Never
# kills a running browser — the whole point is that the Google session survives between runs so
# nobody has to sign in again.
#
# Why a second browser at all: the Playwright MCP holds an exclusive lock on its own Chrome
# profile. When another agent is driving that browser, every Playwright tool fails with
# "Browser is already in use". This instance is independent, so the two never contend.
#
# The profile lives under ~/Documents/sabbatical-finance/ (NOT the public repo, NOT /tmp).
# It holds live Google cookies, so it is deliberately outside anything that gets committed.

set -euo pipefail

PORT=9222
PROFILE="$HOME/Documents/sabbatical-finance/chrome-cdp-profile"
# There are usually SEVERAL stale mcp-chrome-* profiles. Pick the one with the biggest cookie
# jar — that is the live, signed-in one. Taking the first alphabetically seeds an empty profile
# and lands you on a Google sign-in page.
SEED="$(for d in "$HOME/Library/Caches/ms-playwright-mcp/mcp-chrome-"*; do
          [ -f "$d/Default/Cookies" ] && echo "$(stat -f%z "$d/Default/Cookies") $d"
        done | sort -rn | head -1 | cut -d' ' -f2-)"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

if curl -s -m 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
  echo "reusing existing CDP browser on :$PORT"
  exit 0
fi

# First run only: seed the cookie jar from the Playwright profile so Google is already signed
# in. Copying Default/Cookies (not Default/Network/Cookies) does carry the session.
if [ ! -d "$PROFILE" ] && [ -n "$SEED" ]; then
  mkdir -p "$PROFILE/Default"
  cp "$SEED/Local State" "$PROFILE/" 2>/dev/null || true
  for f in "Default/Preferences" "Default/Cookies" "Default/Login Data" "Default/Web Data"; do
    cp "$SEED/$f" "$PROFILE/$f" 2>/dev/null || true
  done
  echo "seeded profile from $SEED"
fi

mkdir -p "$PROFILE"
"$CHROME" --user-data-dir="$PROFILE" --remote-debugging-port=$PORT \
  --no-first-run --no-default-browser-check \
  about:blank >"$HOME/Documents/sabbatical-finance/chrome-cdp.log" 2>&1 &

for _ in $(seq 1 20); do
  sleep 1
  if curl -s -m 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; then
    echo "CDP browser up on :$PORT (profile persists; do not kill it)"
    exit 0
  fi
done
echo "failed to reach CDP on :$PORT — see chrome-cdp.log" >&2
exit 1
