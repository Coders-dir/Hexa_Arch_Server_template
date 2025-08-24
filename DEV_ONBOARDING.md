# Developer onboarding & infra runbook

This file documents a small, dependable developer onboarding flow for the repository and lists actionable improvements for the templates (monolith and microservice) so they are friendly for users adopting the template.

Goals
- Provide a one-command bootstrap for Codespaces / local dev that sets up a local kind cluster, creates the `cd-deployer` role, generates `infra/kubeconfig-sa` and installs Python deps.
- If automation fails, provide a short, fool-proof fallback so a new developer can continue.
- Document shortcomings observed and propose concrete improvements (hexagonal structure, security, CI checks).

Status (automated bootstrap)
- The repository includes `infra/scripts/bootstrap-codespace.sh` which:
  - Requires Docker, `kind`, `kubectl`, and `poetry`.
  - Creates a kind cluster named `hexa-test`.
  - Applies `infra/k8s/cd-deployer-role.yaml` and generates `infra/kubeconfig-sa` and `infra/kubeconfig-sa.b64`.
  - Installs Poetry (if missing) and runs `poetry install` for subprojects.
- During a run in this Codespace I executed the script successfully. The microservice dependencies installed; the monolith `poetry install` failed with a lockfile mismatch (see Troubleshooting below).

Quick start (automated)
1. Ensure you have Docker available in your environment (Codespaces devcontainer should provide it). If you don't run in Codespaces, install Docker.
2. From repo root run:
```bash
bash infra/scripts/bootstrap-codespace.sh
```
3. After success you should have:
  - A Kind cluster `hexa-test` (local) and kubectl context `kind-hexa-test`.
  - Generated `infra/kubeconfig-sa` and `infra/kubeconfig-sa.b64` (base64 encoded). This file contains the service-account token and the CA data.
  - Poetry installed and project dependencies installed for supported subprojects (note: monolith may require `poetry lock` refresh).

Fallback manual steps (if bootstrap fails or you don't have Docker)
- Create the `prod` namespace and SA (if not present):
```bash
kubectl create namespace prod || true
kubectl apply -f infra/k8s/cd-deployer-role.yaml
```
- Generate SA token (on a running cluster) and build a kubeconfig (if `kubectl create token` exists):
```bash
# token: modern clusters
kubectl -n prod create token cd-deployer

# or legacy: find the SA secret name and decode the token
SECRET=$(kubectl -n prod get sa cd-deployer -o jsonpath='{.secrets[0].name}')
kubectl -n prod get secret $SECRET -o jsonpath='{.data.token}' | base64 --decode > sa.token

# build kubeconfig manually (replace SERVER and CA as needed)
kubectl config set-cluster kind-hexa-test --server=https://YOUR_API_SERVER --certificate-authority=/path/to/ca.crt --embed-certs=true --kubeconfig=infra/kubeconfig-sa
kubectl config set-credentials cd-deployer --token="$(cat sa.token)" --kubeconfig=infra/kubeconfig-sa
kubectl config set-context default --cluster=kind-hexa-test --user=cd-deployer --namespace=prod --kubeconfig=infra/kubeconfig-sa
kubectl config use-context default --kubeconfig=infra/kubeconfig-sa
```

Troubleshooting
- `poetry install` for `monolith-template` may fail with:
  - "pyproject.toml changed significantly since poetry.lock was last generated" — fix by running `poetry lock` in `monolith-template` (maintainer task) or regenerate `poetry.lock` from pyproject and commit it.
- If the bootstrap reports `connection refused` when using the generated kubeconfig, ensure the Kind cluster is running (`kind get clusters` and `kubectl cluster-info --context kind-hexa-test`).
- If Docker is unavailable in your environment, use the fallback manual steps and/or run the templates against a remote test cluster.

Security & least privilege
- The generated `infra/kubeconfig-sa` is a namespaced ServiceAccount for `prod` and is intentionally limited by a namespaced `Role` (not ClusterRole). This is a safe default for CD.
- The template should document how to provision a more-privileged account only where necessary and how to rotate the secret.

Immediate developer deliverables (low-risk / high-value)
1. Add this `DEV_ONBOARDING.md` (this file) so devs have a single doc to get started.
2. Add `infra/kubeconfig-sa.b64` to GitHub repo secrets in the target repo (CI) using the `gh` CLI or via UI:
   - `gh secret set KUBE_CONFIG --body-file infra/kubeconfig-sa.b64 --repo OWNER/REPO`
3. Add a short `SECURITY.md` and `CONTRIBUTING.md` that mention handling secrets, token rotation, and minimal RBAC.

Recommended template improvements (medium-term roadmap)
These are recommended changes to make the templates production-ready and clearer for people adopting hexagonal architecture.

- Hexagonal architecture scaffolding (apply consistently across templates):
  - `src/app/adapters/inbound/http/` — controllers / request adapters (already present in parts)
  - `src/app/adapters/outbound/` — DB, message broker, external services adapters
  - `src/app/ports/` — interface definitions for repositories, external services
  - `src/app/usecases/` or `src/app/services/` — application services orchestrating domain logic
  - `src/app/domain/` — pure domain models and business rules
  - `src/app/infra/` — configuration, DB wiring, 3rd party clients
  - Ensure dependency direction: adapters -> ports -> usecases -> domain (core)

- Documentation & examples
  - Add a short `ARCHITECTURE.md` that explains the layers and maps existing repo files to those layers.
  - Provide one example `usecase` with its inbound controller, domain model, and outbound repository to demonstrate the pattern end-to-end.

- Security hardening in templates
  - Input validation and sanitization in controllers (pydantic models and strict parsing; example schemas in `adapters/inbound/http/schemas.py`).
  - Default helmet: rate limiting, CORS policy, request size limits, logging of suspicious requests.
  - Placeholders for authentication middleware (JWT validation) and an example of how to connect with the `cd-deployer` SA for K8s ops.

- CI and QA
  - Add a CI check that ensures `poetry.lock` and `pyproject.toml` are consistent (fail early with a hint to run `poetry lock`).
  - Add basic linters, type checks and security checks (bandit/ruff/mypy) in CI groups for template quality.

- Frontend / Backend separation
  - The templates currently focus on backend (FastAPI). If a frontend is required, add a minimal `frontend/` static site or a separate `ui-template/` with instructions to host it (or point to an example React/Vite template).
  - Document how to run the frontend and backend together via `docker-compose` or with `ingress` in Kubernetes manifests.

Implementation plan (I will execute as CTO now)
1. Persist this `DEV_ONBOARDING.md` into the repo (done).
2. Create `SECURITY.md` with basic secret handling and RBAC notes (I can add this next).
3. Create a short `ARCHITECTURE.md` mapping existing `monolith-template/src` structure to the hexagonal layers and list actionable TODOs.
4. Add a CI check file (small) that verifies `poetry.lock` consistency (propose only; will not commit without your OK, but I can implement it if you want).

If you want me to continue I will:
- Add `SECURITY.md` and `ARCHITECTURE.md` next.
- Optionally scaffold a single example use case in `monolith-template` to demonstrate the hexagonal pattern (very small change, testable).

Notes
- The `infra/scripts/bootstrap-codespace.sh` and `infra/scripts/generate-kubeconfig.sh` are already a good automation fit for Codespaces — they should remain the primary fast path for new devs.
- Where the scripts fail (Poetry lock mismatch) we should prefer to update the lockfile in the repo to keep the template experience smooth for newcomers.

Contact
- As CTO acting on the repo, I've executed the bootstrap in this Codespace and confirmed the generated `infra/kubeconfig-sa` exists and the Kind cluster was created. Next I will add `SECURITY.md` and `ARCHITECTURE.md` unless you instruct otherwise.

---
End of `DEV_ONBOARDING.md`.
