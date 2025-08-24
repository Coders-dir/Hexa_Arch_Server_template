# Monolith integration guide: Postgres (Neon), Supabase, MongoDB Atlas

This document explains how to configure the monolith template to integrate with external DB providers used by the team (Neon/Postgres, Supabase, MongoDB Atlas). It also documents the recommended minimal system and package requirements for developers.

Prerequisites
- Docker (for local development with kind)
- Poetry (for Python dependency management)
- If you plan to build binary dependencies (eg asyncpg) locally, you need system build tools (gcc, python-dev headers):
  - Ubuntu/Debian: `sudo apt-get update && sudo apt-get install -y build-essential python3-dev`

Environment variables (example `.env`)
```
# Postgres (Neon)
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>:<port>/<db>?sslmode=require

# Supabase (REST)
SUPABASE_URL=https://<project>.supabase.co
SUPABASE_API_KEY=eyJ... (anon or service key)

# MongoDB Atlas
MONGO_URI=mongodb+srv://<user>:<pass>@cluster0.xxxxx.mongodb.net/app_db?retryWrites=true&w=majority
```

Supabase
- The repo includes an async HTTP client `src/app/adapters/outbound/supabase_client.py` using `httpx`.
- To test locally without committing keys, set `SUPABASE_URL` and `SUPABASE_API_KEY` in your `.env` and run the app.

Postgres (Neon)
- For production integration, prefer using an async ORM or DB layer (SQLAlchemy async, asyncpg pool managed by DB layer).
- If you need `asyncpg`, ensure system packages are installed before `poetry install` (see Prerequisites).

MongoDB Atlas
- The repo includes a Motor adapter `src/app/adapters/outbound/mongo_user_repo.py`.
- Set `MONGO_URI` in `.env` for local runs.

Testing and CI notes
- Do not store production DB credentials in the repository. Use GitHub secrets and the `infra/kubeconfig-sa` for CD.
- For CI runs that need to exercise integration tests, consider using hosted test databases or ephemeral instances.

Troubleshooting
- If `poetry install` fails while building binary packages (eg asyncpg), install the system build dependencies or use a prebuilt manylinux wheel compatible with your environment.
- If you're in a restricted Codespace where Docker cannot run nested containers, use the manual fallback in `DEV_ONBOARDING.md`.

Local integration tests (optional)
--------------------------------

You can run real Postgres and Mongo locally for integration tests. The repository includes `docker-compose.test.yml` (Postgres 15 + Mongo 6).

Enable the test services by setting the environment variable `RUN_INTEGRATION=1` and run pytest. Example:

```bash
cd monolith-template
RUN_INTEGRATION=1 PYTHONPATH="$PWD" poetry run pytest tests/integration -q
```

This will start the compose services, wait for readiness, set `DATABASE_URL` and `MONGO_URI` env vars for the tests, run tests, then tear down the services.

If Docker is unavailable in your environment, use the mocked integration tests already present in `tests/integration`.


