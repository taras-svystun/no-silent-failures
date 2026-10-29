# Glossary

**no-silent-failures**: a tiny tasks API that cannot break without someone being told.

- **Task**: the one domain object the API stores (create, read, update, delete).
- **Chaos endpoint** (`/chaos`): an endpoint that fails or slows down on purpose, so each alert can be triggered by hand.
- **Dashboard as code**: the Grafana dashboard lives as a JSON file in `grafana/dashboards/`, loaded at start-up, so wiping Grafana loses nothing.
- **Provisioning**: Grafana reading its data sources and dashboards from files at start-up instead of from clicks in the UI.
- **Alert rule**: a PromQL question Prometheus asks every 5 s; if the answer is non-empty for `for:` long, the alert fires.
- **Alertmanager**: the service that turns firing alerts into messages: groups them, waits a bit, sends to Telegram, and sends "resolved" when they stop.
- **Integration test**: a test that runs the app against a real Postgres, so it catches what a fake database would hide (a broken migration, a wrong column).
- **Fixture**: a pytest function that prepares something a test needs (the Postgres container, an empty table) and cleans it up after.
- **CI** (continuous integration): GitHub runs the tests on its own machine on every push, so a broken change shows a red cross before anyone ships it.
- **Dead man's switch**: an alert that always fires and is sent to a service outside the stack; when its messages stop, that outside service raises the alarm. It answers "who watches the watcher". Not built here.
