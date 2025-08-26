#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"
echo "[bootstrap] repo root: $REPO_ROOT"

echo "[bootstrap] starting codespace bootstrap"

# Ensure docker is available
if ! command -v docker >/dev/null 2>&1; then
  echo "[bootstrap] docker not found. In Codespaces devcontainer, Docker should be available via docker-in-docker feature." >&2
  exit 1
fi

export PATH="/usr/local/bin:$PATH"

CLUSTER_NAME=${CLUSTER_NAME:-hexa-test}
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
  echo "[bootstrap] kind cluster $CLUSTER_NAME already exists"
else
  echo "[bootstrap] creating kind cluster $CLUSTER_NAME"
  kind create cluster --name "$CLUSTER_NAME" --wait 120s
fi

echo "[bootstrap] applying infra manifests"
kubectl apply -f infra/k8s/cd-deployer-role.yaml

echo "[bootstrap] generating SA kubeconfig"
chmod +x infra/scripts/generate-kubeconfig.sh
infra/scripts/generate-kubeconfig.sh cd-deployer prod infra/kubeconfig-sa
base64 -w0 infra/kubeconfig-sa > infra/kubeconfig-sa.b64

echo "[bootstrap] installing Python tooling and project dependencies"
# Install poetry if missing
if ! command -v poetry >/dev/null 2>&1; then
  echo "[bootstrap] installing Poetry"
  curl -sSL https://install.python-poetry.org | python3 -
  export PATH="$HOME/.local/bin:$PATH"
fi

for proj in service-template; do
  if [ -f "$proj/pyproject.toml" ]; then
    echo "[bootstrap] installing dependencies for $proj"
    (cd "$proj" && poetry install --no-interaction --no-ansi) || echo "[bootstrap] poetry install failed for $proj"
  fi
done

if [ -n "${GH_TOKEN:-}" ]; then
  echo "[bootstrap] GH_TOKEN present, attempting to set repo secret KUBE_CONFIG (requires rights)"
  if ! command -v gh >/dev/null 2>&1; then
    echo "[bootstrap] gh CLI not found; skipping secret upload" >&2
  else
    REPO=$(git remote get-url origin | sed -E 's#.*[:/](.+/.+)\.git#\1#')
    echo "[bootstrap] uploading secret to $REPO"
    gh secret set KUBE_CONFIG --body-file infra/kubeconfig-sa.b64 --repo "$REPO"
  fi
else
  echo "[bootstrap] GH_TOKEN not provided; skipping secret upload. kubeconfig available at infra/kubeconfig-sa.b64"
fi

echo "[bootstrap] done. To validate, run: gh workflow run validate-kubeconfig.yml -f ref=main or visit Actions -> validate-kubeconfig"

exit 0
