#!/bin/bash
set -e

# ─────────────────────────────────────────────
#  switchboard-chat installer
# ─────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

CLUSTER_NAME="switchboard-chat-cluster"
CALICO_VERSION="v3.28.0"
RELEASE_NAME="switchboard-chat"

# Pass --yes / -y to auto-resolve conflicts (e.g. delete a conflicting kind
# cluster) without prompting — useful for CI or repeat local runs.
FORCE_YES=false
[[ "$1" == "--yes" || "$1" == "-y" ]] && FORCE_YES=true

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info()  { echo -e "${BLUE}[→]${NC} $1"; }
step()  { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }

# ─────────────────────────────────────────────
# 1. Prerequisite checks
# ─────────────────────────────────────────────
check_prereqs() {
  step "Checking prerequisites"

  command -v docker  >/dev/null 2>&1 || error "Docker not found. Install from https://docs.docker.com/get-docker/"
  docker info        >/dev/null 2>&1 || error "Docker daemon is not running. Start Docker first."
  command -v kind    >/dev/null 2>&1 || error "kind not found. Install from https://kind.sigs.k8s.io/"
  command -v kubectl >/dev/null 2>&1 || error "kubectl not found. Install from https://kubernetes.io/docs/tasks/tools/"
  command -v helm    >/dev/null 2>&1 || error "helm not found. Install from https://helm.sh/docs/intro/install/"

  log "Docker:  $(docker --version)"
  log "kind:    $(kind --version)"
  log "kubectl: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
  log "helm:    $(helm version --short)"
}

# ─────────────────────────────────────────────
# 2. Check for host port conflicts (another kind cluster already
#    bound to the ports this cluster needs, e.g. 80/443)
# ─────────────────────────────────────────────
check_port_conflicts() {
  step "Checking for host port conflicts"

  # If our own cluster already exists, kind will just reuse it — nothing to check.
  if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    log "Cluster '${CLUSTER_NAME}' already exists — nothing to check"
    return
  fi

  local ports
  ports=$(grep -oP 'hostPort:\s*\K[0-9]+' kind-config.yaml 2>/dev/null | sort -u)

  if [[ -z "${ports}" ]]; then
    warn "Could not read hostPort values from kind-config.yaml — skipping port check"
    return
  fi

  local conflicting_clusters=()
  local port owner other_cluster c
  for port in ${ports}; do
    # A running container publishing this exact host port, that isn't ours.
    owner=$(docker ps --format '{{.Names}}\t{{.Ports}}' 2>/dev/null \
      | grep -E "(^|[^0-9])${port}->" \
      | awk '{print $1}' \
      | grep -v "^${CLUSTER_NAME}-" || true)

    if [[ -n "${owner}" ]]; then
      other_cluster="${owner%-control-plane}"
      if [[ ! " ${conflicting_clusters[*]} " == *" ${other_cluster} "* ]]; then
        conflicting_clusters+=("${other_cluster}")
      fi
      warn "Host port ${port} is already in use by kind cluster '${other_cluster}' (container ${owner})"
    fi
  done

  if [[ ${#conflicting_clusters[@]} -eq 0 ]]; then
    log "No port conflicts"
    return
  fi

  for c in "${conflicting_clusters[@]}"; do
    if [[ "${FORCE_YES}" == true ]]; then
      warn "--yes set — deleting conflicting cluster '${c}' automatically"
      kind delete cluster --name "${c}"
      log "Cluster '${c}' deleted"
      continue
    fi

    echo ""
    read -p "Delete kind cluster '${c}' to free the port and continue? (y/N): " reply
    if [[ "${reply}" == "y" || "${reply}" == "Y" ]]; then
      info "Deleting cluster '${c}'..."
      kind delete cluster --name "${c}"
      log "Cluster '${c}' deleted"
    else
      error "Port conflict with cluster '${c}' not resolved — aborting. Either delete it yourself (kind delete cluster --name ${c}) or change the hostPort values in kind-config.yaml."
    fi
  done
}

# ─────────────────────────────────────────────
# 3. Create kind cluster
# ─────────────────────────────────────────────
create_cluster() {
  step "Creating kind cluster"

  if kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    warn "Cluster '${CLUSTER_NAME}' already exists — skipping creation"
  else
    info "Creating cluster from kind-config.yaml..."
    kind create cluster --config kind-config.yaml
    log "Cluster '${CLUSTER_NAME}' created"
  fi

  kubectl config use-context "kind-${CLUSTER_NAME}"
  log "kubectl context set to kind-${CLUSTER_NAME}"
}

# ─────────────────────────────────────────────
# 4. Install Calico CNI
# ─────────────────────────────────────────────
install_calico() {
  step "Installing Calico CNI"

  # Check if already installed
  if kubectl get daemonset calico-node -n kube-system >/dev/null 2>&1; then
    warn "Calico already installed — skipping"
    return
  fi

  info "Applying Calico manifests (${CALICO_VERSION})..."
  kubectl apply -f "https://raw.githubusercontent.com/projectcalico/calico/${CALICO_VERSION}/manifests/calico.yaml"

  info "Waiting for Calico node daemonset to be ready (up to 120s)..."
  kubectl rollout status daemonset/calico-node -n kube-system --timeout=120s
  log "Calico CNI ready"
}

# ─────────────────────────────────────────────
# 5. Install nginx ingress controller
# ─────────────────────────────────────────────
install_ingress() {
  step "Installing nginx ingress controller"

  helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx 2>/dev/null || true
  helm repo update >/dev/null 2>&1

  if helm list -n ingress-nginx 2>/dev/null | grep -q ingress-nginx; then
    warn "nginx ingress already installed — skipping"
    return
  fi

  helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
    --namespace ingress-nginx \
    --create-namespace \
    --set controller.service.type=NodePort \
    --set controller.hostPort.enabled=true \
    --set controller.hostPort.ports.http=80 \
    --set controller.hostPort.ports.https=443 \
    --wait --timeout=120s

  log "nginx ingress controller ready"
}

# ─────────────────────────────────────────────
# 6. Build Docker images
# ─────────────────────────────────────────────
build_images() {
  step "Building Docker images"

  info "Building backend:local from src/backend..."
  docker build -t backend:local ./src/backend
  log "backend:local built"

  info "Building frontend:local from src/frontend..."
  docker build -t frontend:local ./src/frontend
  log "frontend:local built"
}

# ─────────────────────────────────────────────
# 7. Load images into kind
# ─────────────────────────────────────────────
load_images() {
  step "Loading images into kind cluster"

  info "Loading backend:local..."
  kind load docker-image backend:local --name "${CLUSTER_NAME}"
  log "backend:local loaded"

  info "Loading frontend:local..."
  kind load docker-image frontend:local --name "${CLUSTER_NAME}"
  log "frontend:local loaded"
}

# ─────────────────────────────────────────────
# 8. Deploy the Helm chart
# ─────────────────────────────────────────────
deploy_chart() {
  step "Deploying Helm chart"

  local value_files=(-f chart/values.yaml)
  if [[ -f chart/values-secrets.yaml ]]; then
    info "Found chart/values-secrets.yaml — layering it over the placeholder dev secrets"
    value_files+=(-f chart/values-secrets.yaml)
  else
    warn "No chart/values-secrets.yaml — using placeholder dev credentials from chart/values.yaml"
    warn "(cp chart/values-secrets.example.yaml chart/values-secrets.yaml to set real ones)"
  fi

  info "Running helm upgrade --install ${RELEASE_NAME} ./chart ..."
  helm upgrade --install "${RELEASE_NAME}" ./chart "${value_files[@]}" --wait --timeout=180s \
    || warn "Helm reported an issue — check with: kubectl get pods -n app -n db"

  log "Helm release '${RELEASE_NAME}' deployed"
}

# ─────────────────────────────────────────────
# 9. Health check
# ─────────────────────────────────────────────
health_check() {
  step "Cluster health check"

  echo ""
  echo "Pods in namespace: app"
  kubectl get pods -n app -o wide 2>/dev/null || echo "  (no pods yet)"

  echo ""
  echo "Pods in namespace: db"
  kubectl get pods -n db -o wide 2>/dev/null || echo "  (no pods yet)"

  echo ""
  echo "Services:"
  kubectl get svc -n app 2>/dev/null
  kubectl get svc -n db  2>/dev/null

  echo ""
  echo "Ingress:"
  kubectl get ingress -n app 2>/dev/null || echo "  (no ingress yet)"

  echo ""
  log "Setup complete!"
  echo ""
  echo -e "  ${GREEN}➜${NC} App:    http://localhost"
  echo -e "  ${GREEN}➜${NC} API:    http://localhost/api"
  echo -e "  ${GREEN}➜${NC} Health: http://localhost/health"
  echo ""
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
main() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  switchboard-chat — install${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  check_prereqs
  check_port_conflicts
  create_cluster
  install_calico
  install_ingress
  build_images
  load_images
  deploy_chart
  health_check
}

main "$@"
