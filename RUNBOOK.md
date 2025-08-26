RUNBOOK — Hexa Arch Server Template

Quick purpose
- This runbook describes the minimal steps to deploy the templates, verify health, and rollback.

Required GitHub repository secrets (used by CD workflows)
- KUBE_CONFIG: base64-encoded kubeconfig for the target cluster (required)
- DATABASE_URL_PROD: production DB connection URL
- JWT_SECRET: JWT signing secret
- GRAFANA_ADMIN_USER (optional): Grafana admin username (default: admin)
- GRAFANA_ADMIN_PASSWORD (optional): Grafana admin password (default: admin)
- ALERT_WEBHOOK_URL (optional): webhook for Alertmanager receiver
- ALERT_SLACK_WEBHOOK (optional): slack webhook URL
- SOPS_AGE_KEY (optional): age private key to decrypt SOPS-encrypted manifests
- SENTRY_DSN (optional)

Quick deploy (GitHub Actions CD)
1. Ensure repository secrets above are set in GitHub (Settings → Secrets).
2. Push a commit to `main` or merge the PR; the CD workflow will run and:
   - decode `KUBE_CONFIG`, create namespace `prod` if missing
   - create `app-secrets` (DATABASE_URL, JWT_SECRET, optional SENTRY_DSN)
   - create `alerting-secrets` if alerting secrets are present
   - create `grafana-admin` secret (use provided or defaults)
   - apply monitoring manifests (Alertmanager, Prometheus, Fluent Bit)
   - apply application manifests

Local smoke test (fast)
- service-template/run_smoke.sh — runs docker-compose locally and checks /health and sample endpoints
- microservices-template/services/user-service/run_smoke.sh — runs the user-service locally

Verification (post-deploy)
- kubectl -n prod get pods
- kubectl -n prod get svc
- kubectl -n prod get deploy,statefulset
- kubectl -n prod logs deploy/alertmanager
- Check Prometheus targets: http://<prometheus-service>:9090/targets
- Grafana available at: https://grafana.example.com (or port-forward)
  - Default admin credentials are from `grafana-admin` secret (defaults: admin/admin).
  - Confirm Prometheus datasource exists and starter dashboard appears.
- Loki: kubectl -n prod get statefulset loki and check PVC bound
- Fluent Bit: check daemonset logs for forwarding errors

Rollback (quick)
- Roll back an application Deployment: kubectl -n prod rollout undo deployment/<name>
- If something is wrong with monitoring, remove the applied manifests and restore previous config from Git (or kube-apiserver):
  - kubectl -n prod delete -f k8s/<manifest.yaml>
- For full rollback to a previous image tag, update the Deployment image and apply, or use your registry/CI tags to redeploy a known-good tag.

Notes & caveats
- This repo includes recommended PoC manifests for Loki/Grafana/Prometheus and basic Alertmanager config. For production:
  - Provide a proper StorageClass and retention policy for Loki.
  - Use runtime-mounted secrets for Alertmanager receivers (we mount `alerting-secrets`).
  - Consider packaging manifests with Helm or Kustomize to manage environments.
  - cert-manager ClusterIssuer `letsencrypt-staging` exists; optionally create `letsencrypt-prod` in your cluster.
- `kubectl --dry-run` validation requires access to a kube-apiserver; CI/CD will validate when a valid `KUBE_CONFIG` is supplied.

Requirements coverage (high level)
- Two templates (Monolith + Microservice): Done
- Local E2E smoke scripts and pytest tests: Done
- CI for tests: Done
- CD to deploy manifests: Done
- Secrets handling and alerting: Done (alerting-secrets mounted at runtime)
- Observability (Prometheus + metrics): Done
- Logging (Fluent Bit -> Loki PoC): Done (persistence: PVC template, tune storageClass in prod)
- Grafana provisioning: Done (datasource + starter dashboard), TLS via cert-manager requires cluster issuer

Contact & handoff
- PR: https://github.com/Coders-dir/Hexa_Arch_Server_template/pull/1
