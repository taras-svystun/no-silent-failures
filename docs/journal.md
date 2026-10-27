# Journal

Newest at the bottom.

- **Plan agreed.** Full scope, 7 steps, design calls recorded in `docs/PLAN.md`.
- **Step 1: service + DB.** FastAPI tasks CRUD, one Alembic migration run by the container entrypoint, `/health` that pings Postgres (503 when it is down, checked by stopping the db container). No DB volume: the data is throwaway, so a volume would be a part with no job.
- **Step 2: metrics + Prometheus.** Middleware counts requests and times them, labelled by route template (unknown URLs go to `unmatched`, so scanners cannot create endless series). No separate error counter: errors are `status=~"5.."` on the one request counter. `db_up` gauge pings the DB on each scrape. Checked: Prometheus target `up`, `db_up` went 1 → 0 → 1 as the db container stopped and started.
- **Step 3: Grafana as code.** Provisioned Prometheus data source (fixed uid `prometheus`) and one dashboard JSON with 4 panels: request rate, error share, p95, DB up/down. Error share uses `or vector(0)`: with no 5xx ever, the error series does not exist and the panel showed "No data" instead of 0. Grafana 13 allows anonymous users only as Viewer, so login stays admin/admin and the port is bound to 127.0.0.1. Checked: `docker compose down && up` brings the dashboard back; with the db stopped, error share 0.42 and `db_up` 0 in both Prometheus and Grafana.
