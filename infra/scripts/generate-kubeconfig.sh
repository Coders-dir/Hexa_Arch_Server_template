#!/usr/bin/env bash
set -euo pipefail
# Usage: ./generate-kubeconfig.sh <serviceaccount> <namespace> <output-file>
# Example: ./generate-kubeconfig.sh cd-deployer prod kubeconfig-sa

SA_NAME=${1:-cd-deployer}
NAMESPACE=${2:-prod}
OUT=${3:-kubeconfig-sa}

CONTEXT=$(kubectl config current-context)
CLUSTER_NAME=$(kubectl config view -o jsonpath='{.contexts[?(@.name=="'"$CONTEXT"'")].context.cluster}')
SERVER=$(kubectl config view -o jsonpath='{.clusters[?(@.name=="'"'$CLUSTER_NAME'"'")].cluster.server}')

# get secret name for SA
SECRET_NAME=$(kubectl -n "$NAMESPACE" get sa "$SA_NAME" -o jsonpath='{.secrets[0].name}')
CA_DATA=$(kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o jsonpath='{.data.ca\.crt}')
TOKEN=$(kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o jsonpath='{.data.token}' | base64 --decode)

# write CA
CA_FILE=$(mktemp)
echo "$CA_DATA" | base64 --decode > "$CA_FILE"

# create kubeconfig
kubectl config --kubeconfig="$OUT" set-cluster "$CLUSTER_NAME" --server="$SERVER" --certificate-authority="$CA_FILE" --embed-certs=true
kubectl config --kubeconfig="$OUT" set-credentials "$SA_NAME" --token="$TOKEN"
kubectl config --kubeconfig="$OUT" set-context default --cluster="$CLUSTER_NAME" --user="$SA_NAME" --namespace="$NAMESPACE"
kubectl config --kubeconfig="$OUT" use-context default

rm -f "$CA_FILE"

echo "wrote $OUT"
