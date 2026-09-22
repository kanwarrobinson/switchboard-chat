# Architecture

## System Overview

A three-tier application running on a local kind Kubernetes cluster:

```
                        ┌──────────────────────────────────────────────┐
                        │              kind cluster                     │
                        │                                               │
  [Browser]             │  ┌─────────────────────────────────────────┐ │
      │                 │  │  nginx ingress controller                │ │
      │ :80/:443        │  │  namespace: ingress-nginx                │ │
      └────────────────►│  └──────────┬──────────────┬───────────────┘ │
                        │             │              │                  │
                        │     path: / │    path:/api │ path:/health    │
                        │             ▼              ▼                  │
                        │  ┌──────────────────────────────────────┐    │
                        │  │           namespace: app              │    │
                        │  │                                       │    │
                        │  │  ┌───────────┐    ┌───────────────┐  │    │
                        │  │  │ frontend  │    │    backend    │  │    │
                        │  │  │ :80       │───►│    :3000      │  │    │
                        │  │  │ nginx     │    │    Node.js    │  │    │
                        │  │  └───────────┘    └───────┬───────┘  │    │
                        │  └──────────────────────────-│──────────┘    │
                        │                              │                │
                        │                    TCP 27017 │                │
                        │                              ▼                │
                        │  ┌───────────────────────────────────────┐   │
                        │  │           namespace: db                │   │
                        │  │                                        │   │
                        │  │  ┌──────────────────────────────────┐ │   │
                        │  │  │  mongodb (StatefulSet)           │ │   │
                        │  │  │  mongodb-0.mongodb.db.svc...     │ │   │
                        │  │  │  PVC: 1Gi                        │ │   │
                        │  │  └──────────────────────────────────┘ │   │
                        │  └────────────────────────────────────────┘  │
                        └──────────────────────────────────────────────┘
```

---

## Components

### Frontend
- **Image**: `frontend:local` (built from `src/frontend/`)
- **Runtime**: nginx:alpine serving static HTML
- **Port**: 80
- **Namespace**: `app`
- **Exposed via**: nginx ingress at path `/`

### Backend
- **Image**: `backend:local` (built from `src/backend/`)
- **Runtime**: Node.js 20 + Express
- **Port**: 3000
- **Namespace**: `app`
- **Exposed via**: nginx ingress at path `/api` and `/health`
- **Connects to**: MongoDB via headless service DNS

### MongoDB
- **Image**: `mongo:7.0` (pulled from DockerHub)
- **Kind**: StatefulSet (stable identity, ordered startup)
- **Port**: 27017
- **Namespace**: `db`
- **DNS**: `mongodb-0.mongodb.db.svc.cluster.local`
- **Storage**: 1Gi PVC (kind default storage class)

---

## Networking

### Ingress
- nginx ingress controller installed via helm
- Host ports 80 and 443 mapped from local machine into kind node
- Routes: `/` → frontend, `/api` → backend, `/health` → backend

### Service DNS
| Service | DNS | Port |
|---------|-----|------|
| frontend | `frontend.app.svc.cluster.local` | 80 |
| backend | `backend.app.svc.cluster.local` | 3000 |
| mongodb | `mongodb-0.mongodb.db.svc.cluster.local` | 27017 |

### Network Policies
- Default deny ingress in both `app` and `db` namespaces
- Explicit allow rules for required traffic only
- See `docs/NETWORK-POLICIES.md` for details

---

## CNI

Calico is used as the CNI plugin (instead of kind's default kindnet) because:
- kindnet has limited NetworkPolicy enforcement
- Calico enforces both ingress and egress policies correctly
- Calico supports cross-namespace network policies

---

## Data Flow

1. User opens `http://localhost` → nginx ingress → frontend pod
2. Frontend HTML loads in browser
3. Browser calls `fetch('/api')` → nginx ingress routes to backend
4. Backend queries MongoDB via `mongodb-0.mongodb.db.svc.cluster.local:27017`
5. Response flows back through the chain
