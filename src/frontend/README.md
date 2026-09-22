# Frontend Service

> **This is starter/example code, not a real app.** It's a plain HTML page
> that proves the ingress → frontend/backend wiring works. Replace it with
> your actual UI (React, Vue, plain HTML, whatever) — see "Replacing with a
> Real Framework" below. Keep serving on port 80 and answering `GET /health`
> with `200 OK`, since the chart's probes and ingress depend on both.

Static HTML served by nginx. Calls the backend `/api` endpoint and displays results.

---

## Files

| File | Purpose |
|------|---------|
| `index.html` | Main UI — shows service status and backend API response |
| `nginx.conf` | nginx server config — serves static files, `/health` probe |
| `Dockerfile` | Builds `frontend:local` image |

---

## How It Works

1. nginx serves `index.html` on port 80
2. The page loads and calls `fetch('/api')` in the browser
3. The nginx **ingress** routes `/api` to the backend service
4. The backend response is displayed on the page

---

## Environment Variables

Set via `chart/values.yaml` (`frontend.env`) — rendered into a ConfigMap by
`chart/templates/app/frontend/configmap.yaml`.

| Variable | Source | Description |
|----------|--------|-------------|
| `APP_ENV` | ConfigMap | Environment name |

---

## Health Check

nginx exposes `/health` returning `200 ok` — used by k8s liveness and readiness probes.

---

## Rebuild and Redeploy

```bash
/rebuild frontend
```

Or manually:
```bash
docker build -t frontend:local ./src/frontend
kind load docker-image frontend:local --name switchboard-chat-cluster
kubectl rollout restart deployment/frontend -n app
```

---

## Replacing with a Real Framework

To replace with React/Vue/etc:
1. Remove `index.html` and `nginx.conf`
2. Add your framework's project files
3. Update `Dockerfile` to build and serve the framework output
4. Keep port 80 for nginx
5. Rebuild and reload: `/rebuild frontend`
