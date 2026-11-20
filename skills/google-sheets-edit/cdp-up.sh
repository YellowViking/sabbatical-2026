#!/usr/bin/env bash
# Bring up (or reuse) a PERSISTENT, debuggable Chrome on CDP port 9222 that can reach
# bot-protected sites (Hyatt/Kasada, and anything else with a JS challenge).
#
#   bash cdp-up.sh                 # start/reuse, pre-warm google + hyatt
#   WARM_URLS="" bash cdp-up.sh    # start without pre-warming
#   bash cdp-up.sh --no-warm
#
# Idempotent: if something is already answering on 9222, it does nothing and exits 0.
# Never kills a running browser — the whole point is that sessions survive between runs.
#
# ---------------------------------------------------------------------------
# WHY THIS SCRIPT IS SHAPED THE WAY IT IS (verified 2026-09-24)
# ---------------------------------------------------------------------------
# 1. PRE-WARM IS MANDATORY for JS-challenge sites.
#    Kasada (hyatt.com) returns HTTP 429 to any navigation issued *while a CDP client
#    is attached*. The page must already be loaded before the agent connects. Proof:
#      - navigate after connectOverCDP   -> 429, empty body
#      - load first, then attach & read  -> 200, full page
#      - load first, then attach & nav   -> 200, full page
#    So we open the warm URLs as Chrome *startup arguments*, then expose the port.
#
# 2. The cookie DB must have a real schema.
#    The previous profile's Default/Cookies was a valid SQLite file with *zero tables*
#    ("schema 0"). A profile that cannot persist cookies can never store the solved
#    challenge token, so it loops on 429 forever. We validate and repair this.
#
# 3. Seed from the REAL Chrome profile, not from Playwright's mcp-chrome-* jars.
#    Those jars are per-session throwaway stores; they hold no site logins.
#
# The profile lives under ~/Documents/sabbatical-finance/ (NOT the public repo, NOT /tmp):
# it holds live cookies, so it stays outside anything that gets committed.

set -euo pipefail

PORT="${CDP_PORT:-9222}"
PROFILE="${CDP_PROFILE:-$HOME/Documents/sabbatical-finance/chrome-cdp-profile}"
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REAL_CHROME_PROFILE="$HOME/Library/Application Support/Google/Chrome"
LOG="$HOME/Documents/sabbatical-finance/chrome-cdp.log"

# Sites to pre-warm. Leave empty to skip (e.g. for spreadsheet-only work).
WARM_DEFAULT="https://www.google.com/ https://www.hyatt.com/"
if [ "${1:-}" = "--no-warm" ]; then WARM_DEFAULT=""; fi
WARM_URLS="${WARM_URLS-$WARM_DEFAULT}"

ok()   { printf '  ok   %s\n' "$1"; }
warn() { printf '  warn %s\n' "$1"; }
die()  { printf '  fail %s\n' "$1" >&2; exit 1; }

port_up() { curl -s -m 2 "http://127.0.0.1:$PORT/json/version" >/dev/null 2>&1; }

# --- 0. already running? -----------------------------------------------------
if port_up; then
  echo "reusing existing CDP browser on :$PORT (no changes made)"
  exit 0
fi

[ -x "$CHROME" ] || die "Chrome not found at: $CHROME"

# --- 1. seed a new profile from the real Chrome profile ----------------------
if [ ! -s "$PROFILE/Default/Cookies" ]; then
  echo "seeding new profile from the real Chrome profile"
  mkdir -p "$PROFILE/Default"
  # Copy the whole Default dir so logins/localStorage come along. COW clone when
  # available (APFS), falling back to a normal copy.
  if ! cp -cR "$REAL_CHROME_PROFILE/Default/." "$PROFILE/Default/" 2>/dev/null; then
    cp -R "$REAL_CHROME_PROFILE/Default/." "$PROFILE/Default/" 2>/dev/null || true
  fi
  cp -c "$REAL_CHROME_PROFILE/Local State" "$PROFILE/Local State" 2>/dev/null \
    || cp "$REAL_CHROME_PROFILE/Local State" "$PROFILE/Local State" 2>/dev/null || true
  ok "seeded from $REAL_CHROME_PROFILE"
fi

# --- 2. validate the cookie DB (the bug that caused endless 429s) ------------
mkdir -p "$PROFILE/Default"
CK="$PROFILE/Default/Cookies"
if [ -f "$CK" ]; then
  tables="$(sqlite3 "$CK" ".tables" 2>/dev/null | tr -s ' ' || true)"
  case "$tables" in
    *cookies*) ok "cookie DB valid ($(sqlite3 "$CK" 'select count(*) from cookies;' 2>/dev/null || echo '?') cookies)" ;;
    *)
      warn "cookie DB has no 'cookies' table (broken) — rebuilding"
      rm -f "$CK" "$CK-journal" "$CK-wal" "$CK-shm"
      if cp -c "$REAL_CHROME_PROFILE/Default/Cookies" "$CK" 2>/dev/null \
         || cp "$REAL_CHROME_PROFILE/Default/Cookies" "$CK" 2>/dev/null; then
        ok "cookie DB rebuilt ($(sqlite3 "$CK" 'select count(*) from cookies;' 2>/dev/null || echo '?') cookies)"
      else
        warn "could not rebuild cookie DB — Chrome will create a fresh one"
      fi
      ;;
  esac
else
  warn "no cookie DB yet — Chrome will create one"
fi

# Drop stale singleton locks so a second instance can start.
rm -f "$PROFILE"/Singleton* 2>/dev/null || true
rm -f "$PROFILE/Default"/Singleton* 2>/dev/null || true

# --- 3. launch WITH the warm URLs as startup args (before any CDP attach) ----
# `--remote-debugging-port` is set at launch, but no CDP client is connected yet, so
# the challenge-bearing navigations below go out as ordinary browser requests.
echo "launching Chrome (pre-warming: ${WARM_URLS:-none})"
# shellcheck disable=SC2086
nohup "$CHROME" \
  --user-data-dir="$PROFILE" \
  --remote-debugging-port="$PORT" \
  --no-first-run \
  --no-default-browser-check \
  ${WARM_URLS} about:blank \
  >>"$LOG" 2>&1 &

for _ in $(seq 1 40); do port_up && break; sleep 0.5; done
port_up || die "Chrome did not expose :$PORT — see $LOG"
ok "CDP up on :$PORT"

# --- 4. let the challenges solve before the agent attaches -------------------
if [ -n "$WARM_URLS" ]; then
  printf '  waiting for challenges to settle'
  for _ in $(seq 1 20); do printf '.'; sleep 1; done
  printf '\n'
  ok "warm pages loaded; safe to attach now"
fi

echo
echo "MCP clients should use:  --cdp-endpoint http://127.0.0.1:$PORT"
echo "Verify with:             node ~/sabbatical/skills/google-maps-saved-places/cdp-check.mjs hyatt.com"
