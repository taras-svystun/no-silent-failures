# no-silent-failures

A tiny tasks API that cannot break without someone being told: FastAPI + Postgres, Prometheus metrics, a Grafana dashboard as code, Alertmanager alerts to Telegram, and pytest integration tests on a real Postgres.

## Run

```sh
cp .env.example .env          # then fill in the Telegram bot token and chat id
docker compose up -d --build  # app on http://localhost:8000 (API docs at /docs)
                              # Prometheus on http://localhost:9090
                              # Grafana on http://localhost:3000 (admin / admin, then "Skip")
docker compose down           # stop everything
```

## Try it

```sh
curl localhost:8000/health
curl -XPOST localhost:8000/tasks -H 'content-type: application/json' -d '{"title":"buy skis"}'
curl localhost:8000/tasks
docker compose stop db && curl -i localhost:8000/health   # 503 "db down"
docker compose start db
curl localhost:8000/metrics                               # raw metrics Prometheus scrapes
open http://localhost:3000/d/service                      # the dashboard, refreshes every 5 s
docker compose rm -sf grafana && docker compose up -d grafana  # wipe Grafana: the dashboard comes back from files
```

## Local dev

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
```
