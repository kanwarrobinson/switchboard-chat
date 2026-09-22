# switchboard-chat

A Kubernetes **base project** — Helm-deployed **Node.js backend**, **nginx
frontend**, and **MongoDB** on a local **kind** cluster, with network
policies and ingress already wired up. `src/backend` and `src/frontend` are
placeholder/example services meant to be replaced; everything else (chart,
namespaces, network policies, ingress, slash commands) is the reusable part.

See [README.md](README.md) for the human-facing pitch and
[docs/CUSTOMIZING.md](docs/CUSTOMIZING.md) for how to retarget this for a new
project.

---

## Project Layout

```
switchboard-chat/
├── AGENTS.md              ← you are here
├── README.md              ← human-facing overview
├── PROGRESS.md            ← current task tracking (read every session)
├── ROADMAP.md             ← project phases and milestones
├── LICENSE
├── install.sh             ← full cluster setup script
├── uninstall.sh           ← soft teardown (keeps the kind cluster)
├── kind-config.yaml       ← kind cluster config (Calico CNI + ingress ports)
│
├── scripts/
│   ├── create-project.sh          ← generate a new project into another folder
│   ├── bootstrap-new-project.sh   ← rename this checkout in place
│   └── lib/rename.sh              ← shared rename logic used by both
│
├── .Codex/
│   ├── settings.json      ← pre-approved commands for Codex
│   └── commands/          ← slash commands
│
├── .github/workflows/     ← CI: build + lint on push/PR
│
├── docs/                  ← architecture, conventions, runbooks
├── src/                   ← EXAMPLE application code — replace this
│   ├── backend/           ← Node.js Express API (placeholder)
│   └── frontend/          ← nginx static frontend (placeholder)
│
└── chart/                 ← Helm chart — the ONE thing that deploys everything
    ├── Chart.yaml
    ├── values.yaml                 ← edit this to retarget images/ports/sizing
    ├── values-secrets.example.yaml ← copy → values-secrets.yaml (gitignored)
    └── templates/
        ├── namespaces.yaml
        ├── app/backend/, app/frontend/
        ├── db/
        ├── network-policies/
        └── ingress.yaml
```

---

## Namespaces

| Namespace | Services |
|-----------|----------|
| `app`     | frontend, backend |
| `db`      | mongodb |

Namespace names are values (`namespaces.app`, `namespaces.db` in
`chart/values.yaml`), not hardcoded — change them there if needed.

---

## Images

| Image | Source | Pull Policy |
|-------|--------|-------------|
| `backend:local` | Built from `src/backend/Dockerfile` | `Never` |
| `frontend:local` | Built from `src/frontend/Dockerfile` | `Never` |
| `mongo:7.0` | DockerHub | `IfNotPresent` |

---

## Quick Start

```bash
./install.sh
```

This creates the kind cluster, installs Calico CNI + nginx ingress, builds
images, loads them into kind, and deploys the Helm chart (`chart/`).

---

## Rebuilding After Code Changes

```bash
# Rebuild backend
docker build -t backend:local ./src/backend
kind load docker-image backend:local --name switchboard-chat-cluster
kubectl rollout restart deployment/backend -n app

# Rebuild frontend
docker build -t frontend:local ./src/frontend
kind load docker-image frontend:local --name switchboard-chat-cluster
kubectl rollout restart deployment/frontend -n app
```

Or use the slash command: `/rebuild backend` or `/rebuild frontend`

If you changed `chart/values.yaml` (ports, resources, env, replicas) rather
than just app code, run `/apply` too.

---

## Slash Commands

| Command | Description |
|---------|-------------|
| `/rebuild <service>` | Rebuild + reload image + restart pod |
| `/apply` | Deploy/update the Helm release from `chart/` |
| `/reset` | Tear down and recreate the entire cluster |
| `/status` | Show pod/service/Helm status across all namespaces |
| `/logs <service>` | Tail logs for a service |
| `/add-service <name>` | Scaffold a new microservice |
| `/debug <pod>` | Diagnose pod/network issues |
| `/netpol` | Explain and inspect network policies |
| `/release` | Full rebuild + deploy pipeline |
| `/progress` | View and update PROGRESS.md |

---

## Key Docs

- `docs/ARCHITECTURE.md` — full system architecture
- `docs/CONVENTIONS.md` — naming, labeling, port rules
- `docs/NETWORK-POLICIES.md` — network topology and policy rules
- `docs/ADDING-A-SERVICE.md` — how to add a new microservice
- `docs/TROUBLESHOOTING.md` — common issues and fixes
- `docs/CUSTOMIZING.md` — turning this base into your own project
- `chart/README.md` — Helm chart structure and values

---

## Always Do at Session Start

1. Read `PROGRESS.md` to know what has been done and what is next
2. Read `docs/CONVENTIONS.md` before creating or modifying any manifest
3. Run `/status` to see current cluster state

---

## Cluster Name

```
switchboard-chat-cluster
```

kubectl context: `kind-switchboard-chat-cluster`

---

## Access the App

After install: **http://localhost**

- `http://localhost/` → frontend
- `http://localhost/api` → backend API
- `http://localhost/health` → backend health check
