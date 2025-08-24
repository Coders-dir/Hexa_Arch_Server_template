## Next development session — prioritized plan (CTO handoff)

Purpose
-------
This document lists the work to be performed in the next development session. It reflects CTO decisions about priorities, what should and should not be implemented now, and acceptance criteria for each item.

Ground rules for the next session
---------------------------------
- No architectural breaking changes without prior approval from the team lead.
- Keep changes small and testable. Each item should include a unit test or a quick integration check.
- Prefer instrumentation and observability over speculative optimization.

Top priorities (do these first)
--------------------------------
1) Move scheduler to a separate worker process
   - Why: avoid in-process background scheduling in app server for production reliability.
   - What to do: extract scheduler loop into a `worker/` entrypoint using the same code path (reuse QuotaManager and queue logic). Add a tiny systemd or Procfile example for local dev and a K8s Job/Deployment manifest for worker.
   - Acceptance criteria: the worker can run locally via `python -m worker` and processes delayed/priority messages as in existing tests; tests remain green.

2) Prometheus metrics & health endpoints
   - Why: production observability (pool size, pool init failures, queue depth, processed jobs count).
   - What to do: add a few Counters/Gauges using `prometheus_client` in `api_key_repo`, `redis_quota`, and scheduler worker. Expose `/metrics` and `/healthz` with lightweight liveness/readiness.
   - Acceptance criteria: `/metrics` returns exposition text and unit tests assert metrics are registered.

3) CI polish and migration robustness
   - Why: reliable CI and reproducible migrations during tests/PRs.
   - What to do: cache Poetry dependencies, ensure migrations are applied in CI container before running tests, add health/wait step for services.
   - Acceptance criteria: CI run completes within time budget and integration tests don't fail due to race conditions.

Do NOT implement yet (deferred)
--------------------------------
- Full multi-datastore HA or production DB tuning — postpone until load tests.
- Replacing Redis with a managed broker or adding Kafka — out of scope for the next session.

Optional / Nice-to-have (lower priority)
---------------------------------------
- Add Grafana dashboard JSONs and basic alerting rules for queue depth and error rate.
- Add automated migration tests that verify DDL forward/backward compatibility.

Credentials & environment notes (sensitive values NOT included)
-----------------------------------------------------------------
- `KUBE_CONFIG`: deploy uses a base64-encoded kubeconfig stored as `KUBE_CONFIG` in GitHub Secrets.
- `DATABASE_URL_PROD`, `JWT_SECRET`, `SOPS_AGE_KEY`: store in GitHub Secrets or a secret manager. Do not commit keys to source.

Suggested branch / PR flow
--------------------------
- Create a feature branch per task: `feature/worker-scheduler`, `feature/metrics`, `ci/polish-migrations`.
- Create small PRs with one major change + tests and a clear description.

Handoff budget
---------------
- This session: no extra prompts allowed. Implement only what's already committed.
- For the next session, allocate tokens/prompts to allow 2–3 prompts (recommended) so I can implement metrics + worker + CI polish.

Contact / Next steps
---------------------
When you open the next session, tell me which of the top priorities to start with (recommended order: worker, metrics, CI). I will open branches, implement changes, add tests and raise PRs.
