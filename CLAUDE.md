# no-silent-failures

A small FastAPI + Postgres service with Prometheus, Grafana and Telegram alerts, tested against a real Postgres, built in 2-3 hours as practice for a Staff AI Infrastructure role.

- `GLOSSARY.md`: the project's words. Use them in code, docs and commits.
- `docs/PLAN.md`: the plan and what we agreed. Read it when starting a step.
- `docs/journal.md`: what each finished step did and why.
- `docs/adr/`: decisions that are hard to undo. Read before changing the stack layout or the alert pipeline.

## Learning lab

Taras is learning production monitoring and integration testing. The AI writes the code; Taras owns the ideas and must be able to explain every piece.

- Explain each new piece at the level of its mechanism: the idea, how the code works step by step, and why it behaves as it does.
- Explanations must be truly simple; length is fine, confusion is not. For each piece: (1) the problem it solves, as a small everyday story; (2) what goes wrong without it, as a concrete scene; (3) only then the technical name and the one line of code. Define every word a beginner would not know (PID, signal, pool, scrape) before using it. One idea per paragraph. Test: could a smart 15-year-old retell it?
- Teach before you test. Order in every step: the material from zero (assume Taras has never heard of it), a worked example he can run and see, then his task with exact actions (where to click, what to type, what he should see), and only then a riddle about what he just learned. Never a riddle or task on something not yet explained.
- Close each step with a short quiz: simple questions on the most fundamental ideas, one idea each, no puzzles. Do not start the next step until the gaps it shows are explained again.
- Tell each step as one story: every piece appears because the previous one needs it ("we did A; A needs B, so B; B causes problem C, so D"). No list of separate facts.
- Keep it small: every file must earn its place. If a part can be thrown away without losing an interview claim or a mechanism, it goes.
- The repo is public. The Telegram bot token and chat id live only in `.env` (git-ignored); `.env.example` holds placeholders.

## Finishing a step

- `README.md` has a copy-paste command for every way to run the project.
- `docker compose up` still starts the whole stack, and `pytest` passes.
