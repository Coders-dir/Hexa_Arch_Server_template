DEMO SLIDES — 5 minute script
=============================

Slide 1 — One line
------------------
FastAPI template with operational scaffolding: queues, quota, scheduler, DB-backed API keys, and reproducible tests.

Slide 2 — Why this exists
-------------------------
- Prevent flaky CI and production surprises by baking retries and local integration early.
- Make it safe to add features rapidly with confidence tests.

Slide 3 — What it contains (point at files)
-------------------------------------------
- `src/app/...` — controllers, adapters, usecases
- `docker-compose.test.yml` — Redis, Postgres, Mongo for tests
- `db/migrations` — DDL for ApiKey table

Slide 4 — Live demo (commands)
------------------------------
Run the quick demo commands from `DEMO.md`.

Slide 5 — Questions & Simplify options
-------------------------------------
- We can remove scheduler/queue for a lean starter.
- We can extract worker & add metrics next session.

Slide 6 — Next steps
---------------------
- See `NEXT_DEVELOPMENT.md` for the prioritized plan.
