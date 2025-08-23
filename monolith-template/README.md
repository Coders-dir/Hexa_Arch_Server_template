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
