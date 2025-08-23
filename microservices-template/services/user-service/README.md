User-service (Hexagonal microservice)

This service is a template showing a single hexagonal microservice using FastAPI.

Deploy

This service includes a CD workflow which will deploy Kubernetes manifests to the `prod` namespace when pushed to `main`.

Required / optional GitHub secrets for CD
- `KUBE_CONFIG` - base64-encoded kubeconfig (required)
- `ALERT_WEBHOOK_URL` - optional webhook URL for Alertmanager; if present the workflow creates a `alerting-secrets` k8s secret.
- `ALERT_SLACK_WEBHOOK` - optional Slack webhook URL for Alertmanager; if present the workflow creates a `alerting-secrets` k8s secret.

Logging
- Fluent Bit is provided; the template assumes a Loki service at `loki:3100`. Update `k8s/fluentbit-configmap.yaml` if you use a different destination.
