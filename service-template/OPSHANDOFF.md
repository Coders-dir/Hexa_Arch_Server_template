OPSHANDOFF: Monolith - Quick Operational Handoff
===============================================

Purpose
-------
This one-page handoff collects the essential run, smoke, and recovery commands for the Monolith template so an operator can verify the service and its dependencies quickly.

Quick facts
-----------
- App entrypoint: `src.app.main:app` (FastAPI)
- Worker entrypoint: `src/app/worker.py`
- Test stack (dev): `docker-compose.test.yml` (Postgres, Mongo, Redis)
- Admin UI (prototype): served at `/admin-ui` (static files under `static/admin-ui`)
- API keys: stored in-memory by default, enable Postgres-backed storage with `USE_DB_KEYS=1` and apply migrations in `db/migrations/`.

Run locally (dev)
-----------------
1. Use the workspace venv Python:

```bash
cd service-template
/workspaces/Hexa_Arch_Server_template/.venv/bin/python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Open health/metrics:

  - Health: http://127.0.0.1:8000/health
  - Metrics: http://127.0.0.1:8000/metrics
  - Admin UI: http://127.0.0.1:8000/admin-ui

Bring up full test stack (Postgres, Mongo, Redis):

```bash
cd monolith-template
docker compose -f docker-compose.test.yml up -d
# (Optional) apply DB migrations for api_keys
cat db/migrations/001_create_api_keys.sql | docker exec -i service-template-postgres-1 psql -U test -d test_db
```

Smoke checks (quick)
--------------------
Run the lightweight smoke script that checks health and admin endpoints:

```bash
cd monolith-template
/workspaces/Hexa_Arch_Server_template/.venv/bin/python scripts/run_postman_smoke.py
```

Manual quick checks (one-liners)

```bash
# Health
curl -fsS http://127.0.0.1:8000/health
# Create an admin token (in python) and call admin API (example):
python - <<'PY'
from src.app.auth import create_access_token
print(create_access_token('ops', role='admin'))
PY
# Use returned token to create/list/revoke api keys via /api/admin/api-keys
```

Secrets & env vars (important)
------------------------------
- `JWT_SECRET` - HMAC secret for admin tokens (set to a secure value in prod)
- `DATABASE_URL` - Postgres DSN for `ApiKeyRepo` (e.g. `postgresql://user:pw@host:5432/db`)
- `MONGO_URI` - Mongo connection string when used
- `USE_DB_KEYS` - Set to `1` to persist API keys in Postgres instead of in-memory store
- `ALLOW_PUBLIC_DOCS` - set to `1` to allow OpenAPI docs in non-dev envs (careful)

Deploy / Rollback (k8s example)
------------------------------
This repo includes example k8s manifests under `k8s/`. A simple deployment flow:

1. Build/push image to registry (CI handles this in `.github/workflows/ci.yml`).
2. Update image tag in your K8s manifest or use `kubectl set image`.
3. Apply manifests:

```bash
kubectl apply -f service-template/k8s/deployment.yaml
kubectl apply -f service-template/k8s/worker-deployment.yaml
```

Rollback (quick):

```bash
# kubectl rollout undo
kubectl rollout undo deployment/hexa-monolith
```

Operational verification (post-deploy)
-------------------------------------
1. Confirm app pods are Ready and passing liveness/readiness probes.
2. Call `/health` on the service endpoint.
3. If using DB-backed keys: run the admin create/list/revoke flow and verify row in Postgres:

```bash
docker exec -i <postgres-pod> psql -U <user> -d <db> -c "SELECT kid, created_at, revoked_at FROM api_keys ORDER BY created_at DESC LIMIT 5;"
```

CI notes
--------
- CI (monolith-template/.github/workflows/ci.yml) now:
  - Installs dependencies via Poetry
  - Runs unit tests
  - Brings up `docker-compose.test.yml`, applies migrations and runs a fast admin UI e2e smoke (`tests/test_admin_ui_e2e.py`)

Recovery tips
------------
- If Postgres migrations fail in CI, inspect logs and retry applying `db/migrations/001_create_api_keys.sql` manually.
- If Redis port conflicts locally, stop other local Redis instances or use a different compose port mapping.

Where to look in repo
---------------------
- App code: `src/app/`
- Admin UI prototype: `static/admin-ui/`
- Worker: `src/app/worker.py` and `k8s/worker-deployment.yaml`
- Migrations: `db/migrations/`
- Tests: `tests/` (includes `test_admin_ui_e2e.py` smoke)

Contact/Follow-up
------------------
If CI shows failures I will triage and open a follow-up branch with fixes; otherwise the next recommended improvements are:
- Convert admin UI prototype to a Vite+React app and add Playwright E2E.
- Harden CI waits and add health checks for more stable integration runs.

Signed-off-by: CTO-mode automated agent
