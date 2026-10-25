# Journal

Newest at the bottom.

- **Plan agreed.** Full scope, 7 steps, design calls recorded in `docs/PLAN.md`.
- **Step 1: service + DB.** FastAPI tasks CRUD, one Alembic migration run by the container entrypoint, `/health` that pings Postgres (503 when it is down, checked by stopping the db container). No DB volume: the data is throwaway, so a volume would be a part with no job.
- **Step 2: metrics + Prometheus.** Middleware counts requests and times them, labelled by route template (unknown URLs go to `unmatched`, so scanners cannot create endless series). No separate error counter: errors are `status=~"5.."` on the one request counter. `db_up` gauge pings the DB on each scrape. Checked: Prometheus target `up`, `db_up` went 1 → 0 → 1 as the db container stopped and started.
