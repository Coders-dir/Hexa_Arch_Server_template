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

# Kubeconfig / Codespace automation

When you open this repository in a GitHub Codespace the devcontainer will run `infra/scripts/bootstrap-codespace.sh` automatically.

What it does

- Creates a local `kind` cluster named `hexa-test` (if missing).
- Applies `infra/k8s/cd-deployer-role.yaml` into the cluster.
- Generates a ServiceAccount kubeconfig at `infra/kubeconfig-sa` and creates a base64 file at `infra/kubeconfig-sa.b64`.
- If `GH_TOKEN` is present in the Codespace environment and the `gh` CLI is available, the script will attempt to set the repository secret `KUBE_CONFIG` automatically.

If you prefer to add the secret manually, copy the contents of `infra/kubeconfig-sa.b64` into the repository secret `KUBE_CONFIG` (Settings → Secrets → Actions → New repository secret).

To manually re-run the bootstrap in the Codespace terminal:

```bash
./infra/scripts/bootstrap-codespace.sh
```
