# /netpol

Explains and inspects the network policies in this cluster.

## Usage

```
/netpol
```

## What traffic is allowed

```
[Internet]
    ↓ port 80/443
[nginx ingress controller] (namespace: ingress-nginx)
    ↓                   ↓
[frontend:80]      [backend:3000]     ← namespace: app
    ↓ (internal)
[backend:3000]
    ↓ port 27017
[mongodb:27017]                        ← namespace: db
```

## Commands to inspect

```bash
# List all network policies
kubectl get networkpolicy --all-namespaces

# Describe policies in app namespace
kubectl describe networkpolicy -n app

# Describe policies in db namespace
kubectl describe networkpolicy -n db
```

## Test connectivity (run a debug pod)

```bash
# Test frontend → backend
kubectl run test --image=busybox --rm -it --restart=Never -n app \
  -- wget -qO- http://backend:3000/health

# Test backend → mongodb
kubectl run test --image=busybox --rm -it --restart=Never -n app \
  -- nc -zv mongodb-0.mongodb.db.svc.cluster.local 27017

# Test that denied traffic is blocked (should timeout)
kubectl run test --image=busybox --rm -it --restart=Never -n db \
  -- wget -qO- http://backend.app.svc.cluster.local:3000/health
```

## Policy templates

| File | Rule |
|------|------|
| `chart/templates/network-policies/app-deny-all.yaml` | Default deny all ingress in app ns |
| `chart/templates/network-policies/db-deny-all.yaml` | Default deny all ingress in db ns |
| `chart/templates/network-policies/allow-frontend-to-backend.yaml` | frontend → backend on 3000 |
| `chart/templates/network-policies/allow-backend-to-mongo.yaml` | backend (app) → mongodb (db) on 27017 |
| `chart/templates/network-policies/allow-ingress-to-app.yaml` | ingress-nginx → frontend:80, backend:3000 |

All five are gated by `networkPolicies.enabled` in `chart/values.yaml` — set it
to `false` there (then `/apply`) to disable enforcement entirely for debugging.
