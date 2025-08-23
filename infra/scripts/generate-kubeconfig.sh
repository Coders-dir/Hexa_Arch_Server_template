#!/usr/bin/env bash
set -euo pipefail
# Usage: ./generate-kubeconfig.sh <serviceaccount> <namespace> <output-file>
# Example: ./generate-kubeconfig.sh cd-deployer prod kubeconfig-sa

SA_NAME=${1:-cd-deployer}
NAMESPACE=${2:-prod}
OUT=${3:-kubeconfig-sa}

# current context and cluster
CONTEXT=$(kubectl config current-context)
if [ -z "$CONTEXT" ]; then
	echo "no current kubectl context; abort" >&2
	exit 2
fi

CLUSTER_NAME=$(kubectl config view -o jsonpath='{.contexts[?(@.name=="'"$CONTEXT"'")].context.cluster}')
if [ -z "$CLUSTER_NAME" ]; then
	echo "could not determine cluster name from context $CONTEXT" >&2
	exit 2
fi

# server and ca (robust jsonpath quoting)
SERVER=$(kubectl config view -o jsonpath='{.clusters[?(@.name=="'"$CLUSTER_NAME"'")].cluster.server}')
CA_DATA=$(kubectl config view -o jsonpath='{.clusters[?(@.name=="'"$CLUSTER_NAME"'")].cluster.certificate-authority-data}')

# Token: prefer `kubectl create token` (works on modern clusters). If not available or fails,
# fall back to reading the SA secret token (legacy clusters).
if kubectl create token --help >/dev/null 2>&1; then
	TOKEN=$(kubectl create token "$SA_NAME" -n "$NAMESPACE" || true)
fi

if [ -z "${TOKEN:-}" ]; then
	# try to find the secret name attached to the SA
	SECRET_NAME=$(kubectl -n "$NAMESPACE" get sa "$SA_NAME" -o jsonpath='{.secrets[0].name}' || true)
	if [ -n "$SECRET_NAME" ]; then
		TOKEN=$(kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o jsonpath='{.data.token}' 2>/dev/null | base64 --decode || true)
		# also prefer CA from the secret if not present
		if [ -z "$CA_DATA" ]; then
			CA_DATA=$(kubectl -n "$NAMESPACE" get secret "$SECRET_NAME" -o jsonpath='{.data.ca\.crt}' 2>/dev/null || true)
		fi
	fi
fi

if [ -z "${TOKEN:-}" ]; then
	echo "failed to obtain token for serviceaccount $SA_NAME in namespace $NAMESPACE" >&2
	exit 3
fi

# write CA
CA_FILE=$(mktemp)
if [ -n "$CA_DATA" ]; then
	echo "$CA_DATA" | base64 --decode > "$CA_FILE"
else
	# fallback: use insecure-skip-tls-verify (not ideal for prod but acceptable for test clusters)
	echo "warning: no CA data found in kubeconfig; creating file but will set --insecure-skip-tls-verify"
	>"$CA_FILE"
fi

# create kubeconfig
kubectl config --kubeconfig="$OUT" set-cluster "$CLUSTER_NAME" --server="$SERVER" ${CA_DATA:+--certificate-authority="$CA_FILE"} --embed-certs=true || true
kubectl config --kubeconfig="$OUT" set-credentials "$SA_NAME" --token="$TOKEN"
kubectl config --kubeconfig="$OUT" set-context default --cluster="$CLUSTER_NAME" --user="$SA_NAME" --namespace="$NAMESPACE"
kubectl config --kubeconfig="$OUT" use-context default

rm -f "$CA_FILE"

echo "wrote $OUT"
