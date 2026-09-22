# Network Policies

---

## Policy Overview

Default posture: **deny all ingress** in both namespaces.  
Explicit allow rules open only the required traffic paths.

```
[ Internet ]
     │
     ▼
[ nginx ingress ]  (ingress-nginx namespace)
     │               │
     ▼               ▼
[ frontend:80 ] → [ backend:3000 ]    ← namespace: app
                       │
                       ▼
                 [ mongodb:27017 ]     ← namespace: db
```

---

## Policies in Effect

### `app-deny-all` (namespace: app)
- **Blocks**: all ingress traffic to every pod in `app` namespace by default
- **File**: `chart/templates/network-policies/app-deny-all.yaml`

### `db-deny-all` (namespace: db)
- **Blocks**: all ingress traffic to every pod in `db` namespace by default
- **File**: `chart/templates/network-policies/db-deny-all.yaml`

### `allow-ingress-to-app` (namespace: app)
- **Allows**: ingress-nginx controller → frontend pod on port 80
- **Allows**: ingress-nginx controller → backend pod on port 3000
- **File**: `chart/templates/network-policies/allow-ingress-to-app.yaml`
- **Selector**: pods with label `app: frontend` or `app: backend`

### `allow-frontend-to-backend` (namespace: app)
- **Allows**: frontend pod → backend pod on port 3000 (in-cluster API calls)
- **File**: `chart/templates/network-policies/allow-frontend-to-backend.yaml`
- **Selector**: backend pod, ingress from frontend pod

### `allow-backend-to-mongo` (namespace: db)
- **Allows**: backend pod (namespace: app) → mongodb pod on port 27017
- **File**: `chart/templates/network-policies/allow-backend-to-mongo.yaml`
- **Cross-namespace**: uses `namespaceSelector` for `app` namespace

---

## Traffic Matrix

| From | To | Port | Allowed? |
|------|----|------|---------|
| Internet | frontend | 80 | ✅ via ingress |
| Internet | backend | 3000 | ✅ via ingress |
| Internet | mongodb | 27017 | ❌ blocked |
| frontend | backend | 3000 | ✅ |
| backend | mongodb | 27017 | ✅ |
| frontend | mongodb | 27017 | ❌ blocked |
| mongodb | backend | any | ❌ blocked |
| backend | frontend | any | ❌ blocked |

---

## Testing Policies

### Verify allowed: backend → mongodb
```bash
kubectl run test --image=busybox --rm -it --restart=Never -n app \
  -- nc -zv mongodb-0.mongodb.db.svc.cluster.local 27017
# Expected: open
```

### Verify blocked: frontend → mongodb
```bash
kubectl run test --image=busybox --rm -it --restart=Never -n app \
  -- nc -zv mongodb-0.mongodb.db.svc.cluster.local 27017
# Wait ~30s — Expected: timeout / connection refused
```

### Verify allowed: frontend → backend
```bash
kubectl run test --image=busybox --rm -it --restart=Never -n app \
  -- wget -qO- http://backend:3000/health
# Expected: JSON health response
```

---

## Important Notes

### DNS (egress not restricted)
In this base setup, only **ingress** is restricted. Egress is open.  
This means all pods can still reach DNS (`kube-dns` on port 53).

To add full egress restriction (Phase 5 hardening), you must add DNS allow rules:
```yaml
egress:
  - ports:
      - port: 53
        protocol: UDP
      - port: 53
        protocol: TCP
```

### Calico Required
NetworkPolicies in this project are enforced by **Calico CNI**.  
If you switch back to kindnet, policies will not be enforced.

### Adding a New Service
When adding a new service via `/add-service <name>`, always add:
1. A new allow rule for who can reach this service
2. Update this document with the new traffic matrix row
