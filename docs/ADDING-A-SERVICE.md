# Adding a New Microservice

Use the `/add-service <name>` command to scaffold automatically, or follow
these steps manually. Everything deploys through the Helm chart in `chart/`
— there is no raw `k8s/` folder to hand-edit per environment.

---

## Step 1 — Create the source folder

```
src/<name>/
├── Dockerfile
├── package.json
├── index.js
└── README.md
```

Copy `src/backend/` as a starting point and rename.

---

## Step 2 — Register the service in chart/values.yaml

Add a new top-level block, modeled on `backend:`:

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
    liveness:
      initialDelaySeconds: 15
      periodSeconds: 10
      failureThreshold: 3
    readiness:
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3
  secret:
    API_KEY: changeme
```

---

## Step 3 — Create the chart templates folder

```
chart/templates/app/<name>/
├── deployment.yaml
├── service.yaml
├── configmap.yaml
└── secret.yaml
```

Copy `chart/templates/app/backend/*.yaml` and replace every
`.Values.backend.*` with `.Values.<name>.*`. For example, `deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.<name>.name }}
  namespace: {{ .Values.namespaces.app }}
  labels:
    app: {{ .Values.<name>.name }}
spec:
  replicas: {{ .Values.<name>.replicas }}
  selector:
    matchLabels:
      app: {{ .Values.<name>.name }}
  template:
    metadata:
      labels:
        app: {{ .Values.<name>.name }}
    spec:
      containers:
        - name: {{ .Values.<name>.name }}
          image: "{{ .Values.<name>.image.repository }}:{{ .Values.<name>.image.tag }}"
          imagePullPolicy: {{ .Values.<name>.image.pullPolicy }}
          ports:
            - containerPort: {{ .Values.<name>.port }}
          envFrom:
            - configMapRef:
                name: {{ .Values.<name>.name }}-config
            - secretRef:
                name: {{ .Values.<name>.name }}-secret
          resources:
            requests:
              memory: {{ .Values.<name>.resources.requests.memory | quote }}
              cpu: {{ .Values.<name>.resources.requests.cpu | quote }}
            limits:
              memory: {{ .Values.<name>.resources.limits.memory | quote }}
              cpu: {{ .Values.<name>.resources.limits.cpu | quote }}
          livenessProbe:
            httpGet:
              path: {{ .Values.<name>.probes.path }}
              port: {{ .Values.<name>.port }}
            initialDelaySeconds: {{ .Values.<name>.probes.liveness.initialDelaySeconds }}
            periodSeconds: {{ .Values.<name>.probes.liveness.periodSeconds }}
          readinessProbe:
            httpGet:
              path: {{ .Values.<name>.probes.path }}
              port: {{ .Values.<name>.port }}
            initialDelaySeconds: {{ .Values.<name>.probes.readiness.initialDelaySeconds }}
            periodSeconds: {{ .Values.<name>.probes.readiness.periodSeconds }}
```

`service.yaml`, `configmap.yaml`, and `secret.yaml` follow the same
find-and-replace off `chart/templates/app/backend/`.

---

## Step 4 — Add a network policy

Create `chart/templates/network-policies/allow-<caller>-to-<name>.yaml`,
wrapped like the others in `{{- if .Values.networkPolicies.enabled }}`:

```yaml
{{- if .Values.networkPolicies.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-<caller>-to-<name>
  namespace: {{ .Values.namespaces.app }}
spec:
  podSelector:
    matchLabels:
      app: {{ .Values.<name>.name }}
  policyTypes:
    - Ingress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: {{ .Values.<caller>.name }}
      ports:
        - port: {{ .Values.<name>.port }}
{{- end }}
```

---

## Step 5 — Add an ingress path (if externally accessible)

Edit `chart/templates/ingress.yaml` and add a new path before the frontend
catch-all:

```yaml
- path: /<name>
  pathType: Prefix
  backend:
    service:
      name: {{ .Values.<name>.name }}
      port:
        number: {{ .Values.<name>.port }}
```

---

## Step 6 — Build and deploy

```bash
/rebuild <name>
# or manually:
docker build -t <name>:local ./src/<name>
kind load docker-image <name>:local --name switchboard-chat-cluster

# then deploy the new chart templates/values:
helm lint ./chart
helm template ./chart -f chart/values.yaml   # sanity-check the render
/apply
```

---

## Step 7 — Update docs

- Add the new service to `docs/ARCHITECTURE.md`
- Add the new port to `docs/CONVENTIONS.md`
- Add the new traffic rule to `docs/NETWORK-POLICIES.md`
- Update `PROGRESS.md`
