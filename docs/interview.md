# Interview notes

## 30-second story

<!-- Taras writes this part, in his own words. Four sentences:
     1. The problem: a service can fail without anyone being told.
     2. What I built: one line on the stack.
     3. How I proved it works: one concrete check.
     4. One thing that surprised me. -->

## Five questions

**1. What do you watch, and why those four alerts?**
The three numbers a user feels: request rate, error share (5xx), and p95 latency. This is the RED method: Rate, Errors, Duration. Plus two "is it alive" checks: Prometheus cannot scrape the app (`up == 0`), and the app cannot reach Postgres (`db_up == 0`). Each alert waits `for: 30s` before it fires, so a single blip stays quiet; in production I would use about 5 minutes. One honest detail: p95 comes from histogram buckets, so it is an estimate. Requests of 1 s showed as p95 2.04 s, because `histogram_quantile` guesses inside the 1-2.5 s bucket.

**2. Why do your metrics use `/tasks/{id}` and not `/tasks/42`?**
Every new label value makes a new time series in Prometheus. With raw paths, each task id, and each URL a bot scans, adds a series, and memory grows without limit. So the middleware labels by route template, and unknown URLs all go to one label, `unmatched`. A test checks both.

**3. How do you know an alert really reaches a person?**
`scripts/demo.sh` runs the whole chain with a deadline on every wait: chaos on, alert firing in Prometheus, sent to Telegram, chaos off, resolved, sent again. It prints which link broke. Two traps I found: Alertmanager's `notifications_total` grows before Telegram answers, so it cannot mean "delivered"; and a run stopped halfway leaves a "resolved" message that the next run would count as its own. The script counts send attempts Telegram accepted, and waits for leftovers to clear. What it cannot prove: that the phone shows the message. A bot cannot read its own messages.

**4. Why test against a real Postgres instead of SQLite or mocks?**
A fake database hides the bugs that matter here: a broken migration, a wrong column type, Postgres-only SQL like `TRUNCATE ... RESTART IDENTITY`. testcontainers starts the same `postgres:17` image that production uses, runs the real Alembic migration, and the whole suite takes about 2 s. The only fake is "is the DB up?" in the one test of `/health` returning 503, because stopping the shared database would break the other tests. GitHub Actions runs it on every push.

**5. Who watches the watcher?**
If Prometheus or Alertmanager dies, every alert goes quiet, and silence looks the same as "all is well". I tried it: with Alertmanager stopped, Prometheus showed `DbDown` firing and only wrote `Error sending alerts` to its own log; no message came. The fix is a dead man's switch: an alert that always fires (`expr: vector(1)`), sent every few minutes to a service outside the stack (for example Healthchecks.io). That service expects the message, and when it stops coming, it alerts by its own path. Not built here: it needs an outside service, and one machine cannot watch itself.

## What I can and cannot claim

Can claim: I set up Prometheus, Grafana (dashboard and data source as code) and Alertmanager with Telegram alerts on a FastAPI + Postgres service, with pytest integration tests on a real Postgres via testcontainers, Alembic migrations, and CI in GitHub Actions. I can explain every alert rule and PromQL query line by line.

Cannot claim: Kubernetes, SLOs and error budgets, monitoring at scale or for many services, on-call experience, or a production incident. This is a one-machine practice project.

What production would add: a dead man's switch, Prometheus storage that survives a restart, two Alertmanagers for high availability, a login in front of every UI, longer `for:` values, and alerts on SLO burn rate instead of fixed thresholds.
