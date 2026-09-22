# /add-service

Scaffolds a new microservice following project conventions.

## Usage

```
/add-service <name>
```

Example: `/add-service payments`

## What it creates

```
src/<name>/
├── Dockerfile
├── package.json
├── index.js
└── README.md

chart/templates/app/<name>/
├── deployment.yaml
├── service.yaml
├── configmap.yaml
└── secret.yaml
```

Plus a new block registered under `chart/values.yaml` (see below) — the
templates read everything from there, they don't hardcode the name/port.

## Rules to follow (from docs/CONVENTIONS.md)

- Namespace: `app`
- Image name: `<name>:local`
- `imagePullPolicy: Never`
- Label: `app: <name>`
- Port: pick an unused port (check existing services first)
- ConfigMap name: `<name>-config`
- Secret name: `<name>-secret`
- Deployment name: `<name>`
- Service name: `<name>` (ClusterIP)

## values.yaml block to add

```yaml
<name>:
  name: <name>
  image:
    repository: <name>
    tag: local
    pullPolicy: Never
  port: <port>
  replicas: 1
  env:
    NODE_ENV: development
  resources:
    requests:
      memory: 64Mi
      cpu: 50m
    limits:
      memory: 128Mi
      cpu: 100m
  probes:
    path: /health
    liveness: { initialDelaySeconds: 15, periodSeconds: 10, failureThreshold: 3 }
    readiness: { initialDelaySeconds: 5, periodSeconds: 5, failureThreshold: 3 }
  secret:
    API_KEY: changeme
```

Model the new `chart/templates/app/<name>/*.yaml` files directly on
`chart/templates/app/backend/*.yaml`, swapping `.Values.backend.*` for
`.Values.<name>.*`.

## After scaffolding

1. Add a network policy allowing traffic to this service:
   `chart/templates/network-policies/allow-<caller>-to-<name>.yaml`
2. Add an ingress path if the service needs external access:
   edit `chart/templates/ingress.yaml`
3. Run `helm lint ./chart && helm template ./chart -f chart/values.yaml` to check it renders
4. Add to `PROGRESS.md` under In Progress
5. Run `/rebuild <name>` to build and load the image, then `/apply` to deploy it
