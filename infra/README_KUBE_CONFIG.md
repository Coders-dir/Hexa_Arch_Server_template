KUBE_CONFIG generation for GitHub Actions CD

This document explains how to create a least-privilege ServiceAccount and generate a kubeconfig suitable for adding as a GitHub Actions secret named `KUBE_CONFIG`.

Steps (operator/admin):

1. Apply the Role, ServiceAccount and RoleBinding (namespace 'prod')

```bash
kubectl apply -f infra/k8s/cd-deployer-role.yaml
```

2. Generate a kubeconfig for the `cd-deployer` service account on your machine that has access to the cluster's kubeconfig and kubectl context.

```bash
infra/scripts/generate-kubeconfig.sh cd-deployer prod kubeconfig-sa
```

3. Base64-encode the kubeconfig and add it to your GitHub repository secrets (or organization secrets) as `KUBE_CONFIG`:

```bash
base64 -w0 kubeconfig-sa > kubeconfig-sa.b64
# Add via GH CLI
gh secret set KUBE_CONFIG --body "$(cat kubeconfig-sa.b64)" --repo OWNER/REPO
```

Notes:
- The manifest `infra/k8s/cd-deployer-role.yaml` creates a namespaced Role and ServiceAccount scoped to `prod`.
- Rotate this secret periodically and monitor Actions logs and deploy audit logs.
