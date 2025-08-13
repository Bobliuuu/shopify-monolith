#!/usr/bin/env bash
set -euo pipefail

# Enhanced setup for local Kubernetes + Airflow debug configuration
# - Optionally starts a local Kubernetes cluster (minikube preferred, kind fallback)
# - Ensures a default StorageClass exists
# - Applies external K8s manifests (no inline YAML)
# - Seeds Airflow Variables expected by the debug DAG
#
# Requirements (install if missing):
#   - kubectl
#   - minikube OR kind + docker
#   - airflow (CLI available in your shell)
#
# Env overrides:
#   START_CLUSTER=true|false           # default true
#   USE_KIND=true|false                # force kind instead of minikube
#   CLUSTER_NAME=shopify-debug         # cluster name
#   MINIKUBE_DRIVER=docker             # or hyperkit, virtualbox, etc
#   NAMESPACE=shopify-debug            # must match manifest unless you edit it
#   PVC_NAME=shopify-duckdb-pvc        # must match manifest unless you edit it
#   AF_DEBUG=true
#   AF_DEBUG_TABLES='["products"]'
#   AF_IMAGE=python:3.10-slim
#   AF_DUCKDB_PATH=/data/data.duckdb
#   AF_NUM_ROWS=1000
#   AF_USE_K8=true
#   AF_REPO_MOUNT_PATH=/workspace
#   AF_SCRIPT_PATH=/workspace/pipeline/sdv.py
#   AF_REQUIREMENTS_PATH=

START_CLUSTER=${START_CLUSTER:-true}
USE_KIND=${USE_KIND:-false}
CLUSTER_NAME=${CLUSTER_NAME:-shopify-debug}
MINIKUBE_DRIVER=${MINIKUBE_DRIVER:-docker}

# Defaults should match the external manifest values
NAMESPACE=${NAMESPACE:-shopify-debug}
PVC_NAME=${PVC_NAME:-shopify-duckdb-pvc}

AF_DEBUG=${AF_DEBUG:-true}
AF_DEBUG_TABLES=${AF_DEBUG_TABLES:-'["products"]'}
AF_IMAGE=${AF_IMAGE:-python:3.10-slim}
AF_DUCKDB_PATH=${AF_DUCKDB_PATH:-/data/data.duckdb}
AF_NUM_ROWS=${AF_NUM_ROWS:-1000}
AF_USE_K8=${AF_USE_K8:-true}
AF_REPO_MOUNT_PATH=${AF_REPO_MOUNT_PATH:-/workspace}
AF_SCRIPT_PATH=${AF_SCRIPT_PATH:-/workspace/pipeline/sdv.py}
AF_REQUIREMENTS_PATH=${AF_REQUIREMENTS_PATH:-}

# Resolve manifest path relative to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
K8S_MANIFEST=${K8S_MANIFEST:-"$REPO_ROOT/pipeline/k8/debug_resources.yaml"}

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "❌ Missing dependency: $1"; exit 1; }
}

maybe_start_minikube() {
  need minikube
  echo "🔧 Starting minikube cluster: $CLUSTER_NAME (driver=$MINIKUBE_DRIVER)"
  minikube status -p "$CLUSTER_NAME" >/dev/null 2>&1 || \
    minikube start -p "$CLUSTER_NAME" --driver="$MINIKUBE_DRIVER"
  kubectl config use-context "minikube"
}

maybe_start_kind() {
  need kind
  need docker
  echo "🔧 Starting kind cluster: $CLUSTER_NAME"
  kind get clusters | grep -q "^$CLUSTER_NAME$" || kind create cluster --name "$CLUSTER_NAME"
  kubectl cluster-info --context "kind-$CLUSTER_NAME"
}

ensure_default_storageclass() {
  # If no default storageclass, try to set one for minikube (standard) or kind (standard)
  if ! kubectl get sc | grep -q '(default)'; then
    echo "ℹ️  No default StorageClass detected. Attempting to set one."
    if kubectl get sc standard >/dev/null 2>&1; then
      kubectl patch storageclass standard -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}' || true
    elif kubectl get sc microk8s-hostpath >/dev/null 2>&1; then
      kubectl patch storageclass microk8s-hostpath -p '{"metadata": {"annotations": {"storageclass.kubernetes.io/is-default-class": "true"}}}' || true
    else
      echo "⚠️  Could not set a default StorageClass automatically. You may need to configure one manually."
    fi
  fi
}

apply_manifests() {
  echo "📄 Applying Kubernetes manifests: $K8S_MANIFEST"
  kubectl apply -f "$K8S_MANIFEST"
}

set_airflow_variables() {
  echo "🛠  Setting Airflow Variables..."
  airflow variables set shopify_debug "$AF_DEBUG"
  airflow variables set shopify_debug_tables "$AF_DEBUG_TABLES"
  airflow variables set shopify_debug_image "$AF_IMAGE"
  airflow variables set shopify_debug_namespace "$NAMESPACE"
  airflow variables set shopify_debug_duckdb_path "$AF_DUCKDB_PATH"
  airflow variables set shopify_debug_num_rows "$AF_NUM_ROWS"
  airflow variables set shopify_debug_use_k8 "$AF_USE_K8"
  airflow variables set shopify_debug_repo_mount_path "$AF_REPO_MOUNT_PATH"
  airflow variables set shopify_debug_script_path "$AF_SCRIPT_PATH"
  if [[ -n "$AF_REQUIREMENTS_PATH" ]]; then
    airflow variables set shopify_debug_requirements_path "$AF_REQUIREMENTS_PATH"
  fi
  airflow variables set shopify_debug_pvc "$PVC_NAME"
}

# --- main ---
need kubectl

if [[ "$START_CLUSTER" == "true" ]]; then
  if [[ "$USE_KIND" == "true" ]]; then
    maybe_start_kind
  else
    if command -v minikube >/dev/null 2>&1; then
      maybe_start_minikube
    elif command -v kind >/dev/null 2>&1; then
      maybe_start_kind
    else
      echo "❌ Neither minikube nor kind is installed. Install one or set START_CLUSTER=false."
      exit 1
    fi
  fi
fi

ensure_default_storageclass
apply_manifests
set_airflow_variables

echo "✅ Local K8s ready. Namespace=$NAMESPACE, PVC=$PVC_NAME. Airflow variables configured."
echo "Next steps:"
echo "  - Ensure Airflow is running (webserver & scheduler)"
echo "  - In Airflow UI, trigger DAG 'shopify_products' with Variable shopify_debug=true" 