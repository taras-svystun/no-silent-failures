# Glossary

**no-silent-failures**: a tiny tasks API that cannot break without someone being told.

- **Task**: the one domain object the API stores (create, read, update, delete).
- **Chaos endpoint** (`/chaos`): an endpoint that fails or slows down on purpose, so each alert can be triggered by hand.
- **Dashboard as code**: the Grafana dashboard lives as a JSON file in `grafana/dashboards/`, loaded at start-up, so wiping Grafana loses nothing.
- **Provisioning**: Grafana reading its data sources and dashboards from files at start-up instead of from clicks in the UI.
