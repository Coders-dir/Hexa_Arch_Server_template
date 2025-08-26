Quick dev handoff for running tests and local integration stack

What this repo provides
- FastAPI app scaffold (hexagonal style)
- Redis-based quota/priority queue + scheduler
- Postgres-backed ApiKey persistence with migrations in `db/migrations`

Quick local run (dev container / codespace)
1. Start the test services used by integration tests:

```bash
cd monolith-template
docker-compose -f docker-compose.test.yml up -d
```

2. (Optional) Apply DB migrations manually if needed:

```bash
# from monolith-template
cat db/migrations/001_create_api_keys.sql | docker exec -i $(docker ps -qf "name=monolith-template-postgres") psql -U test -d test_db
```

3. Run the full test suite (integration tests require RUN_INTEGRATION=1):

```bash
cd monolith-template
export RUN_INTEGRATION=1
poetry install --no-interaction
poetry run pytest -q
```

Quick runtime checks (what I run in CI locally): ping + write/read for each service

- Redis: set/get a key
- Mongo: insert/find a document
- Postgres: create TEMP table + insert/fetch

CI notes
- A minimal GitHub Actions flow is provided at `.github/workflows/ci-integration.yml`.
- The workflow uses services (postgres, redis, mongo) to run integration tests.

Next steps (recommended minimal):
- Add a simple metrics hook for DB pool init failures (increment a stat or structured log).
- Keep the scheduler/worker as a separate process for production; the current in-app scheduler is fine for tests and local dev.

This dev handoff is complete for this session. The prioritized plan for the next session is in `../../NEXT_DEVELOPMENT.md` (root). No further changes will be made in this session.
