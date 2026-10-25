# no-silent-failures

A small FastAPI + Postgres service with Prometheus, Grafana and Telegram alerts, tested against a real Postgres, built in 2-3 hours as practice for a Staff AI Infrastructure role.

- `GLOSSARY.md`: the project's words. Use them in code, docs and commits.
- `docs/PLAN.md`: the plan and what we agreed. Read it when starting a step.
- `docs/journal.md`: what each finished step did and why.
- `docs/adr/`: decisions that are hard to undo. Read before changing the stack layout or the alert pipeline.

## Learning lab

Taras is learning production monitoring and integration testing. The AI writes the code; Taras owns the ideas and must be able to explain every piece.

- Explain each new piece at the level of its mechanism: the idea, how the code works step by step, and why it behaves as it does.
- Open each step with a riddle or a prediction for Taras to make, then reveal the answer.
- Keep it small: every file must earn its place. If a part can be thrown away without losing an interview claim or a mechanism, it goes.
- The repo is public. The Telegram bot token and chat id live only in `.env` (git-ignored); `.env.example` holds placeholders.

## Finishing a step

- `README.md` has a copy-paste command for every way to run the project.
- `docker compose up` still starts the whole stack, and `pytest` passes.
