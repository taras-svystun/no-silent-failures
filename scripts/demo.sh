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

alert_firing() {
  curl -s "$PROM/api/v1/query" \
    --data-urlencode "query=ALERTS{alertname=\"$ALERT\",alertstate=\"firing\"}" |
    grep -q '"alertname"'
}
alert_gone() { ! alert_firing; }

# Telegram messages Alertmanager has sent (success or not) and how many failed.
sent()   { curl -s "$AM/metrics" | awk '/^alertmanager_notifications_total\{integration="telegram"/ {s+=$2} END {print s+0}'; }
failed() { curl -s "$AM/metrics" | awk '/^alertmanager_notifications_failed_total\{integration="telegram"/ {s+=$2} END {print s+0}'; }
sent_more_than() { (( $(sent) > $1 )); }

# A "sent" count also grows when Telegram says no, so check the failures too.
no_new_failures() {
  local new=$(( $(failed) - failed0 ))
  if (( new > 0 )); then
    say "FAILED: $new Telegram sends failed (bad token? docker compose up -d --force-recreate alertmanager)"
    exit 1
  fi
}

[[ -f .env ]] || { echo "No .env: cp .env.example .env and fill in the Telegram bot token and chat id."; exit 1; }

say "starting the stack"
docker compose up -d --build --quiet-pull
wait_for "app healthy" app_healthy
wait_for "Prometheus ready" ready "$PROM"
wait_for "Alertmanager ready" ready "$AM"

sent0=$(sent) failed0=$(failed)

say "chaos on: calling /chaos/error twice a second"
( while true; do curl -s "$APP/chaos/error" >/dev/null; sleep 0.5; done ) &
chaos_pid=$!
trap 'kill $chaos_pid 2>/dev/null || true' EXIT

wait_for "$ALERT firing in Prometheus" alert_firing
wait_for "Telegram message sent (firing)" sent_more_than "$sent0"
no_new_failures
sent1=$(sent)

say "chaos off"
kill $chaos_pid; wait $chaos_pid 2>/dev/null || true  # wait: no "Terminated" line

wait_for "$ALERT gone from Prometheus" alert_gone
wait_for "Telegram message sent (resolved)" sent_more_than "$sent1"
no_new_failures
say "done: 2 Telegram messages sent, 0 failed. Check your phone."
