# Journal

Newest at the bottom.

- **Plan agreed.** Full scope, 7 steps, design calls recorded in `docs/PLAN.md`.
- **Step 1: service + DB.** FastAPI tasks CRUD, one Alembic migration run by the container entrypoint, `/health` that pings Postgres (503 when it is down, checked by stopping the db container). No DB volume: the data is throwaway, so a volume would be a part with no job.
