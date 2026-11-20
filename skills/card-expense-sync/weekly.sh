#!/usr/bin/env bash
# Weekly expense tally — run by launchd every Sunday morning (local time, so it follows the trip
# across time zones).
#
#   bash skills/card-expense-sync/weekly.sh            # run now (Chase only)
#   bash skills/card-expense-sync/weekly.sh --install  # (re)install the Sunday launchd job
#   bash skills/card-expense-sync/weekly.sh --remove   # uninstall it
#
# What a run does: brings up the persistent CDP Chrome if it is not already up (never restarts
# it), opens the Chase tab, and posts a notification asking you to sign in. It then WAITS up to
# 45 minutes. As soon as Chase is signed in it pulls (JSON + the rolling statement CSV),
# categorises, writes the last two complete Sun–Sat weeks to the sheet with the sheet's own
# macro, verifies them, and notifies the week's total.
#
# It cannot sign in for you — bank sessions last ~20 minutes, so they are always dead by the
# next Sunday. If the notification says "N lodging charge(s) need a STAYS rule", ask an agent
# to read the bookings and add them; it writes those nights as one-day spikes until then.
set -uo pipefail

LABEL="com.buyuchen.expense-tally"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/../.." && pwd)"
LOG="$HOME/Documents/sabbatical-finance/weekly.log"   # financial output: outside the public repo

case "${1:-}" in
  --install)
    mkdir -p "$(dirname "$PLIST")"
    cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$HERE/weekly.sh</string><string>--scheduled</string></array>
  <key>StartInterval</key><integer>3600</integer>
  <key>ProcessType</key><string>Interactive</string>
  <key>StandardErrorPath</key><string>$HOME/Library/Logs/$LABEL.launchd.log</string>
</dict>
</plist>
EOF
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$PLIST"
    echo "installed: checks hourly, runs once each Sunday from 10:00 local -> $PLIST"
    exit 0 ;;
  --remove)
    launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
    rm -f "$PLIST"; echo "removed $LABEL"; exit 0 ;;
esac

# Scheduling: launchd fires this HOURLY and the script decides. launchd's own calendar keeps the
# time zone it booted with — the first two Sunday runs fired at 19:07 CEST, i.e. 10:07 Pacific —
# while `date` here follows the Mac's current zone. So: run on Sunday from 10:00 *local*, once per
# ISO week (a stamp file; a run that ended without signing in is not retried that day).
if [ "${1:-}" = "--scheduled" ]; then
  STAMP="$HOME/Documents/sabbatical-finance/.weekly-$(date +%G-W%V)"
  [ "$(date +%u)" = 7 ] && [ "$(date +%H)" -ge 10 ] && [ ! -e "$STAMP" ] || exit 0
  touch "$STAMP"
fi

# launchd starts with a bare PATH; node lives in Homebrew.
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
mkdir -p "$(dirname "$LOG")"
{
  echo "=== $(date '+%Y-%m-%d %H:%M %Z') ==="
  bash "$REPO/skills/google-sheets-edit/cdp-up.sh" --no-warm
  # Chase only: the Amex Platinum is rarely used on this trip, and a missed Amex charge isn't
  # lost — the ledger unions every sync, so it lands whenever Amex is next pulled by hand
  # (`cdp-sync.mjs --write`, both banks).
  node "$HERE/cdp-sync.mjs" --banks chase --write --wait-login 45 --notify
  echo "exit $?"
} >> "$LOG" 2>&1
