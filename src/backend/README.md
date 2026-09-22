# Backend Service

> **This is starter/example code, not a real app.** It exists to prove the
> platform (Deployment, probes, Service, network policies, ingress) works
> end-to-end. Replace the routes in `index.js` with your actual API — keep
> the `Dockerfile`'s exposed port and the `GET /health` contract, since the
> chart's probes and the ingress path rules depend on them.

Node.js + Express API. Connects to MongoDB.

---

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness/readiness probe — returns db connection state |
| GET | `/api` | Basic info endpoint |
| GET | `/api/items` | Placeholder — replace with real business logic |

---

## Environment Variables

Set via `chart/values.yaml` (`backend.env`, `backend.port`) and
`backend.secret` (real values go in `chart/values-secrets.yaml`, see
`chart/README.md`) — rendered into a ConfigMap/Secret by
`chart/templates/app/backend/{configmap,secret}.yaml`.

| Variable | Source | Description |
|----------|--------|-------------|
| `PORT` | ConfigMap | Server port (default: 3000) |
| `NODE_ENV` | ConfigMap | Environment name |
| `MONGO_HOST` | ConfigMap | MongoDB pod DNS |
| `MONGO_PORT` | ConfigMap | MongoDB port |
| `MONGO_DB` | ConfigMap | Database name |
| `MONGO_USERNAME` | Secret | MongoDB root username |
| `MONGO_PASSWORD` | Secret | MongoDB root password |
| `MONGO_URI` | Secret | Full MongoDB connection string |

---

## Local Development (outside k8s)

```bash
cd src/backend
npm install
MONGO_URI=mongodb://root:rootpassword@localhost:27017/appdb npm start
```

---

## Rebuild and redeploy

```bash
/rebuild backend
```

Or manually:
```bash
docker build -t backend:local ./src/backend
kind load docker-image backend:local --name switchboard-chat-cluster
kubectl rollout restart deployment/backend -n app
```

---

## Adding new routes

Add new routes to `index.js` following the same pattern.  
When adding a new resource, create a separate file (e.g., `routes/items.js`) and require it in `index.js`.
