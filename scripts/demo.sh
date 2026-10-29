#!/usr/bin/env bash
# The whole chain in one command: chaos -> metric -> alert -> Telegram -> resolved.
# Each wait has a deadline, so the demo itself cannot hang or fail silently.
set -euo pipefail
cd "$(dirname "$0")/.."

APP=http://localhost:8000
PROM=http://localhost:9090
AM=http://localhost:9093
ALERT=HighErrorRate
DEADLINE=180  # seconds per wait; firing takes about 1 min, resolving about 2

say() { echo "[$(date +%H:%M:%S)] $*"; }

# wait_for "what we wait for" command...: retry every 2 s until it succeeds.
wait_for() {
  local what=$1; shift
  local start=$SECONDS
  say "waiting: $what"
  until "$@"; do
    if (( SECONDS - start > DEADLINE )); then
      say "FAILED: no '$what' after $DEADLINE s"
      exit 1
    fi
    sleep 2
  done
  say "ok: $what ($((SECONDS - start)) s)"
}

app_healthy() { curl -sf "$APP/health" >/dev/null; }
ready() { curl -sf "$1/-/ready" >/dev/null; }

# alert_is firing / alert_is pending|firing: does Prometheus show it in that state?
alert_is() {
  curl -s "$PROM/api/v1/query" \
    --data-urlencode "query=ALERTS{alertname=\"$ALERT\",alertstate=~\"$1\"}" |
    grep -q '"alertname"'
}
alert_firing() { alert_is firing; }
alert_quiet() { ! alert_is 'pending|firing'; }

# Telegram send attempts, both counted after Telegram answers
# (alertmanager notify/retry_stage.go). alertmanager_notifications_total is
# no good here: it grows before the first attempt, and its failed twin only
# after all retries, about 30 s later.
tg() { curl -s "$AM/metrics" | awk -v m="^alertmanager_notification_$1" 'index($0, "{integration=\"telegram\"}") && $0 ~ m {s+=$2} END {print s+0}'; }
attempts() { tg requests_total; }
failed()   { tg requests_failed_total; }
delivered() { echo $(( $(attempts) - $(failed) )); }

# Wait condition: a new message reached Telegram. Any failed attempt stops
# the demo at once, so a bad token cannot pass as "sent".
delivered_more_than() {
  local new=$(( $(failed) - failed0 ))
  if (( new > 0 )); then
    say "FAILED: Telegram refused $new send attempts (bad token? docker compose up -d --force-recreate alertmanager)"
    exit 1
  fi
  (( $(delivered) > $1 ))
}

[[ -f .env ]] || { echo "No .env: cp .env.example .env and fill in the Telegram bot token and chat id."; exit 1; }

say "starting the stack"
docker compose up -d --build --quiet-pull
wait_for "app healthy" app_healthy
wait_for "Prometheus ready" ready "$PROM"
wait_for "Alertmanager ready" ready "$AM"

# A run that stopped halfway leaves the alert on, and its late "resolved"
# message would be counted as ours. Let it clear, then give Alertmanager one
# group_interval (30 s) to send that message.
if ! alert_quiet; then
  wait_for "$ALERT left from an earlier run to clear" alert_quiet
  say "waiting 30 s for Alertmanager to send its last message"
  sleep 30
fi

failed0=$(failed) delivered0=$(delivered)

say "chaos on: calling /chaos/error twice a second"
( while true; do curl -s "$APP/chaos/error" >/dev/null; sleep 0.5; done ) &
chaos_pid=$!
trap 'kill $chaos_pid 2>/dev/null || true' EXIT

wait_for "$ALERT firing in Prometheus" alert_firing
wait_for "Telegram message delivered (firing)" delivered_more_than "$delivered0"
delivered1=$(delivered)

say "chaos off"
kill $chaos_pid; wait $chaos_pid 2>/dev/null || true  # wait: no "Terminated" line

wait_for "$ALERT gone from Prometheus" alert_quiet
wait_for "Telegram message delivered (resolved)" delivered_more_than "$delivered1"
say "done: 2 Telegram messages delivered, 0 refused. Check your phone."
