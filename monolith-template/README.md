NOTICE: This monolith template content has been migrated to `service-template/README.md`.
Please prefer `service-template/README.md` for the canonical documentation. This file is kept as an archive and compatibility layer during migration.

````markdown
Monolithic Hexagonal Template (FastAPI)
Monolithic Hexagonal Template (FastAPI)

Overview
This is a production-ready template for a Modular Monolith following Hexagonal (Ports & Adapters) architecture using FastAPI.

Highlights
- FastAPI ASGI app with a sample `user` module (domain, application, ports, adapters)
- Pydantic settings-based config
- Dockerfile + docker-compose for local development (Mongo included)
- GitHub Actions CI/CD templates
- Kubernetes manifest and secret template
- `.env.example` and mapping to GitHub secrets

Quick start (local)
1. Copy `.env.example` to `.env` and fill values.
2. Start services:

```bash
docker compose up --build
```

This template is intended to be copy-pasted and adapted per project.

Required GitHub secrets (create under Settings → Secrets → Actions)
- DATABASE_URL_STAGING — staging DB URL (map from your MONGO_URI_2 if using Mongo, or Postgres URL)
- DATABASE_URL_PROD — production DB URL (map from MONGO_URI_3)
- DB_MIGRATION_URL — admin DB URL for migrations (map from MONGO_URI_ADMIN)
- JWT_SECRET — JWT signing secret
- SENTRY_DSN — optional Sentry DSN
- DOCKER_REGISTRY / DOCKER_REGISTRY_PASSWORD — credentials for image push (GHCR/ECR)
- KUBE_CONFIG — base64-encoded kubeconfig for CD workflow (or use cloud provider creds)
 - ALERT_WEBHOOK_URL — optional webhook URL for Alertmanager receiver (used by CD to create k8s secret `alerting-secrets`)
 - ALERT_SLACK_WEBHOOK — optional Slack webhook URL for Alertmanager Slack receiver (CD will create `alerting-secrets`)

Logging
- Fluent Bit is included as a DaemonSet. By default it is configured to send logs to a Loki service at `http://loki:3100` (see `k8s/fluentbit-configmap.yaml`). If you don't run Loki, change the `fluentbit-config` output section or provide a Loki endpoint via your cluster service.

Local quick commands
- Copy env example:

```bash
cp .env.example .env
# edit .env
```

- Start local dev stack (Mongo + app):

```bash
make up
```
Handoff: what we delivered
--------------------------

Vision
~~~~~~
This template is a production-oriented modular-monolith implementing Hexagonal (Ports & Adapters) principles. The goal is to make business logic independent from framework and infrastructure, enable safe refactors, and add reproducible enforcement so policy (architecture, API contract, dependency lockfile) is measured continuously.

What we implemented
~~~~~~~~~~~~~~~~~~~
- Enforcement tooling: AST-based architecture checker (`monolith-template/tools/arch_check.py`) to enforce allowed import boundaries.
- OpenAPI generation and contract validation: `monolith-template/tools/generate_openapi.py` and `monolith-template/tools/contract_check.py` generate the app OpenAPI and compare it with `contracts/expected_openapi.json`.
- Lockfile check scaffold: `monolith-template/tools/lockfile_check.py` (CI-friendly script to ensure `poetry.lock` is updated when dependencies change).
- Stable CI-friendly tests: added direct pytest wrappers under `monolith-template/tests` that run enforcement checks reliably in CI.
- Local test ergonomics: implemented `tests/fake_redis.py` (an in-memory Redis emulation) and `tests/conftest.py` patches so developers can run the test suite without external services by default.
- Tests & docs: added focused unit tests for the fake Redis (`tests/test_fake_redis_unit.py`) and a `tests/README.md` documenting how to run tests locally and the fake Redis limitations.
- Repo hygiene: removed accidental code-fence artifacts in Python/feature files and added compatibility re-exports for adapters during refactors.
- Automation: `monolith-template/tools/run_tests.sh` (helper) and a lightweight GitHub Actions workflow (`.github/workflows/monolith-enforce.yml`) to run enforcement checks on PRs against `main`.

Why these changes
~~~~~~~~~~~~~~~~~
The intent was to make the repository safe to refactor and to provide early, automatic feedback about architectural drift and API/contract regressions. By keeping enforcement checks fast and deterministic (faking external services where appropriate), developer iteration time is reduced and CI shows clear policy pass/fail signals.

How to validate locally (quick)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. Set PYTHONPATH and run the helper (fast):

```bash
export PYTHONPATH=$(pwd)/monolith-template
bash monolith-template/tools/run_tests.sh
```

2. Run full tests (optional):

```bash
export RUN_FULL_TESTS=1
python -m pytest monolith-template/tests -q
```

Files of interest
~~~~~~~~~~~~~~~~~
- `monolith-template/tools/arch_check.py`  — architecture import rules enforcement
- `monolith-template/tools/generate_openapi.py` — generates `src/app/openapi.json`
- `monolith-template/tools/contract_check.py` — compares generated OpenAPI to `contracts/expected_openapi.json`
- `monolith-template/tools/lockfile_check.py` — lockfile enforcement helper
- `monolith-template/tools/run_tests.sh` — wrapper to run enforcement checks and tests consistently
- `monolith-template/tests/fake_redis.py` — in-memory Redis emulation for local runs
- `monolith-template/tests/test_fake_redis_unit.py` — unit tests for the fake redis
- `monolith-template/tests/README.md` — testing docs

Operational notes and next steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- CI: the branch `refactor/organize-adapters` contains a PR workflow that runs the enforcement checks on PRs to `main`. Open the PR from that branch to trigger Actions.
- Expand fakes carefully: the fake Redis covers the commands used by the quota/circuit-breaker helpers; add more behaviours if future tests require them and cover them with unit tests.
- Move more adapters incrementally: when reorganizing adapters, prefer a re-export stub to avoid breaking imports, run `tools/arch_check.py` and `tools/run_tests.sh` after each small change.
- Consider placing enforcement rules in a centralized `docs/` or `infra/` folder and creating a `make enforce` target to unify commands.

Where to hand off
~~~~~~~~~~~~~~~~~
Assign reviewers that understand Hexagonal architecture and CI (suggested roles: lead engineer, SRE, API owner). Provide the following context to reviewers:

- Goals: ensure adapter refactors are non-breaking and that API contract and architecture rules are continuously validated.
- How to review: run `tools/run_tests.sh`, inspect `monolith-template/tools/*` scripts, and check `tests/README.md` for local reproduction.

Final notes
~~~~~~~~~~~
This handoff focuses on being pragmatic: enforceable tooling, reproducible tests, and low-friction developer experience. If you want, I will continue by opening the PR, triaging CI failures (if any), and proceeding to the next adapter refactor and its tests.

- Run tests:

```bash
make test
```

Migration notes
- This template defaults to Mongo for fast setup. If you prefer Postgres, the repo includes a small Alembic skeleton under `infra/migrations/postgres/` to adapt. For Mongo, use migration scripts or a managed migration tool (mongo-migrate, Mongock) per project.

Migration guide (POC/MVC -> Hexagonal)
1. Identify business entities in your MVC app (e.g., User, Order). For each entity, create a folder under `src/app/domain/` and move domain logic there.
2. Create use-cases under `src/app/application/usecases/` for each operation (create_user, find_user).
3. Define repository ports in `src/app/ports/` (interfaces only).
4. Implement outbound adapters under `src/app/adapters/outbound/` (DB, cache).
5. Implement inbound adapters under `src/app/adapters/inbound/` (HTTP controllers). Wire controllers to use-cases, not data-layer directly.
6. Move settings to `src/app/infra/config.py` and remove direct ENV usage throughout code.
7. Add integration tests under `tests/integration/` that exercise real DB via docker-compose.

CI/CD notes
- Protect `main` branch and enable `Environments` in GitHub for `staging` and `production` with required reviewers and secrets.
- Use the CD workflow to create k8s secrets from GitHub secrets at deploy time (implemented in `.github/workflows/cd.yml`).

How secrets map to existing repository variables
- MONGO_URI_1 -> DATABASE_URL_DEV
- MONGO_URI_2 -> DATABASE_URL_STAGING
- MONGO_URI_3 -> DATABASE_URL_PROD
- MONGO_URI_4 -> optional (analytics/replica)
- MONGO_URI_ADMIN -> DB_MIGRATION_URL

Environments & production secrets (operational)
 - Create GitHub Environments for `staging` and `production` (Repository → Settings → Environments).
 - Add required secrets to each Environment (e.g., `DATABASE_URL_PROD`, `JWT_SECRET`, `KUBE_CONFIG`). Environment secrets are only available to workflows that reference that environment.
 - Protect the `production` environment with required reviewers and a wait-for-approval rule so deploys require explicit sign-off.

GHCR image tagging and cleanup policy
 - CI will push images to GHCR as `ghcr.io/<owner>/hexa-monolith:<sha>`; the `latest` tag is optional. Use short, immutable tags (commit SHA) for deploys.
 - To clean up images, use `gh api --method DELETE /user/packages/container/<package-name>/versions/<version-id>` or the GitHub UI. Consider an automated retention policy in your registry.

Secrets encryption & Vault guidance
 - For repo-level encrypted secrets, consider SOPS with age or KMS; include an `infra/secrets/README.md` if you adopt it.
 - For larger orgs, prefer HashiCorp Vault or a cloud secrets manager and reference secrets via the CD pipeline instead of storing them in the repo.
