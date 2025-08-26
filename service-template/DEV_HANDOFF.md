Quick dev handoff for running tests and local integration stack

What this repo provides
...

Quick dev handoff for running tests and local integration stack

What this repo provides
- FastAPI app scaffold (hexagonal style)
- Redis-based quota/priority queue + scheduler
- Postgres-backed ApiKey persistence with migrations in `db/migrations`

Quick local run (dev container / codespace)
1. Start the test services used by integration tests:

```bash
cd service-template
docker-compose -f docker-compose.test.yml up -d
```

2. (Optional) Apply DB migrations manually if needed:

```bash
# from monolith-template
cat db/migrations/001_create_api_keys.sql | docker exec -i $(docker ps -qf "name=service-template-postgres") psql -U test -d test_db

# cd into the canonical template for further developer steps
cd service-template
```

3. Run the full test suite (integration tests require RUN_INTEGRATION=1):

```bash
cd service-template
export RUN_INTEGRATION=1
poetry install --no-interaction
poetry run pytest -q
```

Quick runtime checks (what I run in CI locally): ping + write/read for each service


CI notes

Next steps (recommended minimal):

This dev handoff is complete for this session. The prioritized plan for the next session is in `../../NEXT_DEVELOPMENT.md` (root). No further changes will be made in this session.
