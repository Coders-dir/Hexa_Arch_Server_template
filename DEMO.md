## Quick demo & plain-language walkthrough

Purpose
-------
This short demo document shows the minimal steps to run the project locally, plus a plain-language explanation of the main components. Use it to present the template in 5 minutes.

One-line summary
----------------
A development-ready FastAPI server template with optional building blocks (Redis queue & quota, Postgres ApiKey storage, scheduler and tests) designed to make local dev and CI reliable.

Quick demo (copy/paste)
----------------------
Start the local test stack and run the tests (this proves the main pieces integrate):

```bash
cd monolith-template
docker-compose -f docker-compose.test.yml up -d
export RUN_INTEGRATION=1
poetry install --no-interaction
poetry run pytest -q
```

If you want a faster smoke check (no tests):

```bash
cd monolith-template
docker-compose -f docker-compose.test.yml up -d
poetry run python - <<'PY'
import asyncio, os
from src.app.adapters.outbound.api_key_repo import get_metrics
print('metrics:', get_metrics())
PY
```

Plain-language map (for a 2-min explanation)
-------------------------------------------
- Hexagonal layout: think of the app as a house. Inbound doors are HTTP controllers; outbound doors are database or cache adapters. The core (usecases/services) contains the house rules.
- Redis quota & priority queue: Redis counts and prioritizes incoming work; high-priority items jump the queue.
- Scheduler & worker: A background runner that wakes scheduled items when their time arrives (currently in-app for local dev; recommended to run as a separate worker in prod).
- ApiKeyRepo (Postgres): secure storage for API keys. The repo code includes robust pool initialization and a per-call fallback to avoid connection storms during startup.
- Tests & docker-compose.test.yml: reproducible local integration stack (Redis, Postgres, Mongo) used by tests and CI.

What’s essential vs optional (if you must simplify)
--------------------------------------------------
- Essential: FastAPI app, at least one datastore, basic tests, `docker-compose.test.yml` for reproducible local runs.
- Optional (can remove to simplify): Redis-based scheduler/priority queue and advanced metrics. The ApiKeyRepo pool backoff can be replaced by simple connect logic if you accept less robustness.

Short talking points to explain to colleagues
-------------------------------------------
- "We scaffolded common operational concerns early (retries, queueing, scheduler) to save time debugging flaky CI and production surprises later." 
- "If the team prefers a minimal starter, we can remove the scheduler and queue in a small PR; nothing is permanently locked in." 
- "This template trades a bit of upfront complexity for a reliable developer experience and faster root-cause debugging later."

5-minute demo script (presenter notes)
------------------------------------
1. Show the file tree for `service-template` (point at `src/app`, `db/migrations`, `docker-compose.test.yml`).
2. Run the quick demo commands above and show tests passing.
3. Open `src/app/adapters/outbound/api_key_repo.py` and explain: "this is the safe for API keys; it retries the DB pool on startup so services don't cascade-fail during restarts." 
4. Show `tests/test_priority_queue.py` to illustrate the priority queue behavior (optional).
5. Conclude: "If we want a leaner template, remove scheduler/queue and keep the rest; if we want production-ready, next session: extract worker & add metrics." Refer to `NEXT_DEVELOPMENT.md` for the prioritized plan.

Where to find this doc
----------------------
- `DEMO.md` (root) — this file
- `monolith-template/DEV_HANDOFF.md` — developer handoff (linked to this demo)

Extras
------
- `DEMO_HANDOUT.md` — one-page handout for distribution during the demo
- `DEMO_SLIDES.md` — simple slide-style markdown you can present or paste into slides
