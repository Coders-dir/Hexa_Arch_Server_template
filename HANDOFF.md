Handoff Summary — Hexagonal Server Templates

This document summarizes the current repository state, required secrets, deploy steps, remaining tasks, and an estimated minimal prompt plan for final handoff.

1) Current state (snapshot)
- Two independent templates:
  - `monolith-template/` — FastAPI hexagonal monolith, Dockerfile, docker-compose, pytest tests, k8s manifests (app, redis, nginx, prometheus, alertmanager, fluentbit), GitHub Actions CI and CD.
  - `microservices-template/services/user-service/` — FastAPI user microservice with its own k8s manifests, docker-compose, tests, CI and CD.
- Local E2E smoke scripts and pytest tests included and verified previously in the dev container.
- CD workflows render Alertmanager config at deploy time when `ALERT_WEBHOOK_URL` secret is present and create `alerting-secrets` k8s secret.
- Prometheus and Alertmanager manifests added to both templates. Prometheus rules exist as both PrometheusRule CR and a rules ConfigMap (for non-Operator setups).

2) Required repository / environment secrets (GitHub Actions)

| Secret | Typical source / provider | Subscription (paid / free) | Where to find it (web UI / docs) |
|---|---|---:|---|
| KUBE_CONFIG | Kubernetes cluster provider (GKE, EKS, AKS) or self-hosted cluster | Depends on provider (GCP/AWS/Azure paid tiers available; self-hosted free) | GKE: https://cloud.google.com/kubernetes-engine/docs/how-to/cluster-access-for-kubectl ; EKS: https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html ; AKS: https://learn.microsoft.com/azure/aks/kubeconfig |
| DATABASE_URL_PROD | Managed DB (AWS RDS, Cloud SQL, Azure DB), or self-hosted Postgres/MySQL | Depends on provider (managed DBs typically paid) | RDS: https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.html ; Cloud SQL: https://cloud.google.com/sql/docs/mysql/connect-admin |
| JWT_SECRET | Generated secret (recommended: long random string). Example generator: jwtsecrets.com | Free | jwtsecrets.com — generate a secure token; or generate locally: `openssl rand -hex 32` |
| GHCR credentials | GitHub Container Registry (GHCR) — use GitHub username & PAT or GITHUB_TOKEN in Actions | Free for public; private packages subject to GitHub plan | https://docs.github.com/en/packages/working-with-a-github-packages-registry/about-github-container-registry |
| ALERT_WEBHOOK_URL | Receiver webhook (Slack Incoming Webhook, generic HTTP webhook, PagerDuty, etc.) | Depends on provider (Slack has free tier) | Slack: https://api.slack.com/messaging/webhooks ; PagerDuty: https://support.pagerduty.com/docs |
| SOPS_AGE_KEY | age key used by SOPS for encrypted manifests (generated locally) | Free (open-source) | SOPS docs: https://github.com/ProtonMail/gopenpgp or https://github.com/containers/skopeo; age docs: https://age-encryption.org/ |
| SENTRY_DSN | Sentry project DSN from Sentry.io project settings | Sentry has free tier | https://docs.sentry.io/product/sentry-basics/dsn-explainer/ |

JWT secret example (free generator)

Example JWT secret (DO NOT USE IN PRODUCTION — rotate before use):

```
46869a7b1a2d2a75081def16b7f1244e162cbeeee9ec206ee918f82dab7642e5
```


3) Deploy (what CD does)
- Push to `main` triggers CD.
- CD decodes `KUBE_CONFIG`, creates namespace `prod`, creates `app-secrets` and optionally `alerting-secrets`, optionally decrypts SOPS files, then applies manifests in this order: alertmanager config -> alertmanager deployment/service -> prometheus config/rules/configmap -> prometheus deployment/service -> application deployment/service.

4) Remaining high-value items (recommended)
- Add real Alertmanager receivers (Slack/email) and verify secret handling. Current approach renders a webhook URL into a ConfigMap at deploy time.
- Configure Fluent Bit output (Loki/Elasticsearch/Cloud) — Fluent Bit manifest present but destination not configured.
- Add Grafana dashboards and optionally a Prometheus scrape/recording rules package.
- Harden RBAC, PodSecurity policies, NetworkPolicies (initial RBAC/NetworkPolicy added; review per cluster policy).
- Implement global rate-limiting if required (recommend Traefik/Kong for multi-replica coordinated limits; NGINX alone is local to Ingress controller replica).
- Move manifests to Helm or Kustomize for environment parameterization and safer templating.
- Add integration tests for CD (dry-run checks) and automations to validate SOPS rendering and secret provisioning.

5) Minimal on-prem validation status
- K8s client-side `kubectl apply --dry-run=client` could not validate against a cluster in this environment; YAML files were parsed and created locally but server-side validation requires a reachable kube-apiserver.

6) Handoff plan & estimated prompts to finish (minimal)
I will finish the remaining items autonomously if you want, but here is a minimal prompt plan to reach a production-ready handoff you can accept:
- Prompt 1 (this turn): Confirm I should produce final artifacts (I created `HANDOFF.md`) and proceed to add Alertmanager receiver templates + Fluent Bit output wiring and Grafana dashboards. If yes, I will implement them.
- Prompt 2: I create a final review PR (or branch) with all changes, and generate a short runbook with exact GitHub secret names and the deploy checklist. You review and request any minor adjustments.
- Prompt 3: Final sign-off and I provide the PR link and a one-page ops handoff (commands to trigger deploy, smoke-test checklist, rollback steps).

Estimated prompts: 1–3 (I can complete everything in 2 prompts if you accept the receiver choices and logging destination I pick — otherwise up to 3 for review/adjustment).

7) Immediate next actions I have completed or will run now
- Created `HANDOFF.md` in repo root (this file).
- Render pipeline & CD updates already implemented to render Alertmanager config at deploy time.
- Prometheus + Alertmanager deployments and services added for both templates.

This file is a snapshot handoff. For the next development session see `NEXT_DEVELOPMENT.md` which lists prioritized tasks, acceptance criteria, and credentials notes.

This session is a handoff: no further prompts are allowed in this session. To continue, open a new session and reference `NEXT_DEVELOPMENT.md`.

