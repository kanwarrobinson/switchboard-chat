# Conventions

Follow these rules when creating or modifying any file in this project.

---

## Namespaces

| Namespace | Used for |
|-----------|----------|
| `app` | All application services (frontend, backend, future microservices) |
| `db` | All databases (MongoDB, future databases) |
| `ingress-nginx` | nginx ingress controller (managed by helm) |

---

## Naming

### Services (app namespace)
| Resource | Pattern | Example |
|----------|---------|---------|
| Deployment | `<name>` | `backend` |
| Service | `<name>` | `backend` |
| ConfigMap | `<name>-config` | `backend-config` |
| Secret | `<name>-secret` | `backend-secret` |

### Database (db namespace)
| Resource | Pattern | Example |
|----------|---------|---------|
| StatefulSet | `<name>` | `mongodb` |
| Headless Service | `<name>` | `mongodb` |
| Secret | `<name>-secret` | `mongodb-secret` |

---

## Labels

Every pod template **must** have these labels:

```yaml
labels:
  app: <service-name>        # required — used by Services and NetworkPolicies
```

Optional recommended labels:

```yaml
labels:
  app: <service-name>
  version: "1.0"
  component: backend         # backend | frontend | database
```

---

## Ports

| Service | Port |
|---------|------|
| frontend | 80 |
| backend | 3000 |
| mongodb | 27017 |
| New services | Start from 3001, increment by 1 |

---

## Image Naming

| Service | Image tag |
|---------|-----------|
| backend | `backend:local` |
| frontend | `frontend:local` |
| new service | `<name>:local` |

### imagePullPolicy rule

```yaml
# For locally built images (backend, frontend, new services)
imagePullPolicy: Never

# For public images (mongo, nginx, etc.)
imagePullPolicy: IfNotPresent
```

---

## File Organization

Everything deploys through the Helm chart in `chart/`. Each service under
`chart/templates/app/` has its own folder with exactly 4 files:

```
chart/templates/app/<name>/
├── deployment.yaml    ← Deployment only
├── service.yaml       ← Service only
├── configmap.yaml     ← ConfigMap only
└── secret.yaml        ← Secret only
```

Do not combine multiple resources in one file. Values that differ per
service (name, port, image, resources, probe settings) belong in
`chart/values.yaml`, not hardcoded in the template — that's what makes this
usable as a base project for other services and other forks. See
`chart/README.md`.

---

## Resource Requests & Limits

Always set requests and limits:

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "50m"
  limits:
    memory: "128Mi"
    cpu: "100m"
```

Adjust based on actual usage. Never leave these blank.

---

## Health Probes

All deployments must have both probes:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: <port>
  initialDelaySeconds: 10
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: <port>
  initialDelaySeconds: 5
  periodSeconds: 5
```

Backend must expose `GET /health` returning `200 OK`.

---

## Secrets

- Use `stringData` (not `data`) for readability in this base project
- Never commit real credentials — `chart/values.yaml` ships placeholder values only
- Real values go in `chart/values-secrets.yaml` (gitignored) — copy it from
  `chart/values-secrets.example.yaml`, see `chart/README.md`
- In production: replace with Vault, sealed-secrets, or external-secrets-operator
- MongoDB default credentials: `root` / `rootpassword` (dev-only placeholder)

---

## Kubernetes API Versions

Use these stable API versions:

| Resource | apiVersion |
|----------|-----------|
| Deployment | `apps/v1` |
| StatefulSet | `apps/v1` |
| Service | `v1` |
| ConfigMap | `v1` |
| Secret | `v1` |
| Namespace | `v1` |
| NetworkPolicy | `networking.k8s.io/v1` |
| Ingress | `networking.k8s.io/v1` |
