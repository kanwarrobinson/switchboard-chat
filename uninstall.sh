#!/bin/bash
set -e

# ─────────────────────────────────────────────
#  switchboard-chat uninstaller (soft)
#  Removes all k8s resources + local images.
#  Kind cluster stays running.
# ─────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

CLUSTER_NAME="switchboard-chat-cluster"
RELEASE_NAME="switchboard-chat"

log()   { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
info()  { echo -e "${BLUE}[→]${NC} $1"; }
step()  { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }

# ─────────────────────────────────────────────
# Confirm
# ─────────────────────────────────────────────
confirm() {
  echo ""
  echo -e "${YELLOW}This will:${NC}"
  echo "  • Uninstall the '${RELEASE_NAME}' Helm release (namespaces app, db + everything in them)"
  echo "  • Uninstall nginx ingress controller"
  echo "  • Remove Docker images: backend:local, frontend:local"
  echo ""
  echo -e "${GREEN}This will NOT:${NC}"
  echo "  • Delete the kind cluster (still running after)"
  echo "  • Touch any project files or manifests"
  echo ""

  # Skip prompt if --yes flag passed
  if [[ "$1" == "--yes" ]]; then
    warn "--yes flag set, skipping confirmation"
    return
  fi

  read -p "Continue? (y/N): " confirm
  echo ""
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
  fi
}

# ─────────────────────────────────────────────
# Check cluster is reachable
# ─────────────────────────────────────────────
check_cluster() {
  step "Checking cluster"

  if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
    warn "Cluster '${CLUSTER_NAME}' not found — skipping k8s cleanup"
    return 1
  fi

  kubectl config use-context "kind-${CLUSTER_NAME}" >/dev/null 2>&1
  log "Cluster '${CLUSTER_NAME}' is reachable"
  return 0
}

# ─────────────────────────────────────────────
# Uninstall the Helm release (cascades namespaces + everything in them)
# ─────────────────────────────────────────────
uninstall_chart() {
  step "Uninstalling Helm release '${RELEASE_NAME}'"

  if helm status "${RELEASE_NAME}" >/dev/null 2>&1; then
    info "Uninstalling '${RELEASE_NAME}' (deletes namespaces app, db and everything in them)..."
    helm uninstall "${RELEASE_NAME}"
    log "Helm release '${RELEASE_NAME}' removed"
  else
    warn "Helm release '${RELEASE_NAME}' not found — skipping"
  fi
}

# ─────────────────────────────────────────────
# Uninstall nginx ingress controller
# ─────────────────────────────────────────────
uninstall_ingress() {
  step "Removing nginx ingress controller"

  if helm list -n ingress-nginx 2>/dev/null | grep -q ingress-nginx; then
    info "Uninstalling ingress-nginx via helm..."
    helm uninstall ingress-nginx -n ingress-nginx
    kubectl delete namespace ingress-nginx --timeout=60s 2>/dev/null || true
    log "nginx ingress controller removed"
  else
    warn "nginx ingress not found — skipping"
  fi
}

# ─────────────────────────────────────────────
# Remove local Docker images
# ─────────────────────────────────────────────
remove_images() {
  step "Removing local Docker images"

  if docker image inspect backend:local >/dev/null 2>&1; then
    docker rmi backend:local
    log "backend:local removed"
  else
    warn "backend:local not found — skipping"
  fi

  if docker image inspect frontend:local >/dev/null 2>&1; then
    docker rmi frontend:local
    log "frontend:local removed"
  else
    warn "frontend:local not found — skipping"
  fi
}

# ─────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────
summary() {
  step "Summary"

  echo ""
  echo "  Namespaces:"
  kubectl get namespace app db 2>/dev/null || echo "  (none — confirmed deleted)"

  echo ""
  echo "  Docker images:"
  docker images | grep -E "backend|frontend" || echo "  (none — confirmed removed)"

  echo ""
  echo "  Kind cluster:"
  kind get clusters 2>/dev/null | grep "${CLUSTER_NAME}" && \
    echo -e "  ${GREEN}✓${NC} '${CLUSTER_NAME}' still running" || \
    echo -e "  ${YELLOW}!${NC} cluster not found"

  echo ""
  log "Uninstall complete."
  echo ""
  echo -e "  Run ${CYAN}./install.sh${NC} to reinstall from scratch."
  echo ""
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
main() {
  echo ""
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  switchboard-chat — uninstall (soft)${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  confirm "$1"

  if check_cluster; then
    uninstall_chart
    uninstall_ingress
  fi

  remove_images
  summary
}

main "$@"
