# Roadmap

---

## Phase 1 — Base Cluster Setup ✅ *(current)*

**Goal:** A working local kind cluster with placeholder services, MongoDB, and network policies.

- [x] kind cluster with Calico CNI
- [x] nginx ingress controller
- [x] `app` namespace — frontend + backend
- [x] `db` namespace — MongoDB StatefulSet
- [x] Network policies (default deny, explicit allow)
- [x] Claude project setup (CLAUDE.md, commands, docs)
- [x] Helm chart (`chart/`) replacing raw manifests — parametrized via `values.yaml`
- [x] Base-project scaffolding — root README, LICENSE, `.gitignore`, `scripts/bootstrap-new-project.sh`, `docs/CUSTOMIZING.md`
- [ ] First successful `./install.sh` run (against the new Helm-based flow)
- [ ] All pods healthy

---

## Phase 2 — Real Application Code

**Goal:** Replace placeholder code with actual backend API and frontend UI.

- [ ] Implement real backend API routes
- [ ] Connect backend to MongoDB with a real schema
- [ ] Build real frontend UI
- [ ] Add environment-specific config (dev vs staging)
- [ ] Add input validation to backend
- [ ] API documentation (OpenAPI/Swagger)

---

## Phase 3 — CI/CD Pipeline

**Goal:** Automate build, test, and deploy.

- [x] GitHub Actions workflow — builds both images, `helm lint`/`helm template`, backend tests (`.github/workflows/ci.yml`)
- [ ] Push built images to a real registry
- [ ] Automated deploy on merge (target environment is project-specific — no shared kind cluster to deploy to in CI)
- [ ] Real integration tests beyond `npm test --if-present`
- [ ] Linting and code quality checks beyond what CI currently runs

---

## Phase 4 — Observability

**Goal:** See what the app is doing.

- [ ] Prometheus + Grafana via helm
- [ ] Backend metrics endpoint (`/metrics`)
- [ ] MongoDB exporter
- [ ] Dashboards for pod health, request rates, error rates
- [ ] Centralized logging (Loki or ELK)
- [ ] Alerting rules

---

## Phase 5 — Production Hardening

**Goal:** Make it production-ready.

- [ ] Full egress network policy enforcement (with DNS allow)
- [ ] Secrets management (Vault or sealed-secrets)
- [ ] Pod security standards (restricted)
- [ ] Resource quotas per namespace
- [ ] Horizontal Pod Autoscaler (HPA) for backend
- [ ] MongoDB replica set (3 nodes)
- [ ] Backup strategy for MongoDB PVC
- [ ] TLS termination at ingress (cert-manager)
- [ ] RBAC — ServiceAccounts per deployment

---

## Future Ideas

- Multi-cluster setup
- Istio service mesh
- GitOps with ArgoCD or Flux
- External secrets operator
