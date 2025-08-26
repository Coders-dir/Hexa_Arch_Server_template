DEMO: One-page handout
======================

Purpose
-------
Quick reference you can hand to a colleague during the 5-minute demo. Includes commands, key files, and short talking points.

Commands (copy/paste)
---------------------
Start local test stack and run tests:

```bash
cd service-template
docker-compose -f docker-compose.test.yml up -d
export RUN_INTEGRATION=1
poetry install --no-interaction
poetry run pytest -q
```

Quick smoke (no tests):

```bash
cd monolith-template
docker-compose -f docker-compose.test.yml up -d
poetry run python - <<'PY'
from src.app.adapters.outbound.api_key_repo import get_metrics
print('metrics:', get_metrics())
PY
```

Key files to show (1 minute)
- `src/app/adapters/outbound/api_key_repo.py`: DB pool init & fallback
- `src/app/adapters/outbound/redis_quota.py`: quota logic (Redis)
- `tests/test_priority_queue.py`: priority queue behavior
- `docker-compose.test.yml`: local integration stack

What to say (elevator points)
- "We built for reliability: retries, pool safety, and a reproducible test stack so CI and local dev behave similarly."
- "We can simplify later: remove scheduler/queue if you want a minimal starter."

What to avoid in the demo
- Don't dive into implementation details of the Lua scripts; focus on behavior and guarantees (priority, atomic pop).
