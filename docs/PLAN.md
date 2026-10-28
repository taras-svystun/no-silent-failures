# Plan

## Purpose

Build a FastAPI + Postgres service that starts with `docker compose up`, is scraped by Prometheus, shown on a Grafana dashboard defined as code, alerts to Telegram through Alertmanager, and is tested with pytest against a real Postgres in GitHub Actions. Afterwards Taras can honestly say: "I set up Prometheus and Grafana with Telegram alerts on a FastAPI service, with pytest integration tests on a real Postgres."

## What we agreed

- Full scope, nothing cut. Time (2-3 h) is the second priority.
- Not a bag of tools: each part must be one the project cannot exist without. Each part below has a "why": what breaks without it.
- The AI writes the code and the PromQL. Taras must read and explain the PromQL (step 2) and drafts the interview story (step 7).
- Each step opens with: a riddle, Taras's task, the AI's task. Both run in parallel; nobody blocks the other.
- Alert `for:` is 30 s for the demo; the real-world value (about 5 min) sits next to it in a comment.
- The repo stays public. Secrets live only in `.env`.

## Design calls (AI's, record here; hard-to-undo ones go to `docs/adr/`)

- **Sync SQLAlchemy + psycopg 3**, not async. FastAPI runs sync endpoints in a thread pool, so it is fast enough here and half the concepts.
- **Raw `prometheus_client` + a ~20-line middleware**, not an instrumentation library. Taras sees every metric being made; one less dependency.
- **Label requests by route template** (`/tasks/{id}`), never the raw path (`/tasks/42`). Raw paths make a new time series per id and can kill Prometheus.
- **DB up/down as a gauge the service sets on each scrape**, not a `postgres_exporter` container. One less service. Drawback accepted: if the service is down we cannot see the DB; the "service down" alert covers that case.
- **Migrations run in the container entrypoint** (`alembic upgrade head && uvicorn`), not a separate migrate job. Drawback accepted: with several replicas they would race; we have one.
- **Alertmanager's built-in Telegram receiver**, no relay bot. The token and chat id reach it as Docker Compose secrets made from `.env` (files in `/run/secrets/`, read with `bot_token_file` / `chat_id_file`), not by rewriting the config with a script. Alertmanager does not read env vars in its config.
- **`/chaos` is two stateless endpoints** (`/chaos/error`, `/chaos/slow`): chaos lasts as long as someone calls them, so "stop chaos" is just stopping the loop. No on/off switch to forget.

## Steps

Each step ends with a checkpoint, a journal line, a commit and a push.

1. **Service + DB.** FastAPI tasks CRUD, SQLAlchemy model, one Alembic migration, `/health` that pings the DB, `docker compose up` brings up app + Postgres.
   Why: without a service there is nothing to watch.
   Taras: create the Telegram bot, fill `.env`.
2. **Metrics + Prometheus.** `/metrics` with request count, latency histogram, error count by endpoint and status; Prometheus scrapes it.
   Why: without numbers, failures are silent.
   Taras: read and explain the PromQL for request rate, error rate and p95 latency (changed on 2026-10-27: understanding over syntax; he gets queries from the AI when needed).
3. **Grafana as code.** Provisioned datasource and dashboard JSON: request rate, p95, error rate, DB up/down.
   Why: humans read pictures faster than queries; "as code" means the dashboard survives a wiped volume.
4. **Alerts → Telegram + `/chaos`.** Rules for high error rate, high p95, service down, DB down; Alertmanager sends to Telegram; `/chaos` makes 500s and slow responses.
   Why: a dashboard nobody looks at is still a silent failure.
5. **Tests + CI.** Unit tests for pure logic; integration tests on a real Postgres via testcontainers, running the real migration; GitHub Actions runs them on every push.
   Why: proves the service works before it ships, against the same database it runs on.
6. **Demo script.** `scripts/demo.sh`: start the stack, fire `/chaos`, wait for the alert in Telegram, stop chaos, wait for "resolved".
7. **Interview notes.** `docs/interview.md`: 30-second story, 5 questions with short answers, what Taras can and cannot claim.
