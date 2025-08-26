Service Template (hexagonal)
===========================

This folder contains the hexagonal server template. It was formerly named `monolith-template` but is intended to be reused for single-service or monolith-style projects that follow hexagonal architecture.

Quick start (Codespaces-friendly)
--------------------------------
1. Open in GitHub Codespaces.  
2. Read the top-level `PROJECT_CONTEXT.md` for vision and roles.  
3. Run unit tests with `poetry run pytest` inside `service-template` if you have Poetry installed. Heavy integration requires remote CI or a developer machine with Docker.

Architecture mandate
--------------------
All code in this folder follows hexagonal architecture: adapters (inbound/outbound), ports, usecases/services, domain. Any divergence requires an ADR and Architect signoff.

Migration note
--------------
The full template contents currently live in `monolith-template/`. A future PR will migrate and reconcile files into this folder; for now use `monolith-template/` as the canonical source for template contents.

Monolith template summary (merged)
---------------------------------
This template is a production-ready modular monolith example using FastAPI and the Hexagonal (Ports & Adapters) pattern. It includes:

- FastAPI app skeleton and example `user` module.
- Dockerfile + `docker-compose` for local dev.
- GitHub Actions CI and CD skeletons.
- Kubernetes manifests and `infra` helpers.
- Enforcement tools: `tools/arch_check.py`, `tools/generate_openapi.py`, `tools/contract_check.py`, and `tools/lockfile_check.py`.

Quick local commands
--------------------
- Copy env example:

```bash
cp .env.example .env
# edit .env
```

- Start local dev stack (if Docker available):

```bash
docker compose up --build
```

- Run enforcement checks and tests (Codespaces-friendly):

```bash
export PYTHONPATH=$(pwd)/service-template
bash service-template/tools/run_tests.sh
```

Where to find enforcement tools
--------------------------------
- `service-template/tools/arch_check.py` — architecture import rules enforcement
- `service-template/tools/generate_openapi.py` — generates OpenAPI
- `service-template/tools/contract_check.py` — compares generated OpenAPI to `contracts/expected_openapi.json`
- `service-template/tools/lockfile_check.py` — lockfile enforcement helper

Operational notes
-----------------
- For heavy integration tests and canary deploys use CI or a dedicated test cluster; Codespaces may not provide Docker or kind by default.
- Protect `main` with branch protection rules and require CODEOWNERS approvals for sensitive paths.

