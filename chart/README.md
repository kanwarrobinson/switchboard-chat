# Helm Chart

The Helm chart that deploys everything under the `app` and `db` namespaces —
this replaced the old raw `k8s/` manifest folder so the whole project can be
retargeted (image names, ports, resource sizing, secrets) by editing one file
instead of dozens.

---

## Structure

```
chart/
├── Chart.yaml
├── values.yaml                    — the file you edit
├── values-secrets.example.yaml    — copy to values-secrets.yaml (gitignored) for real creds
└── templates/
    ├── namespaces.yaml
    ├── app/
    │   ├── backend/                — configmap, secret, deployment, service
    │   └── frontend/                — configmap, secret, deployment, service
    ├── db/                          — mongodb secret, headless service, statefulset
    ├── network-policies/            — deny-all defaults + allow rules
    └── ingress.yaml
```

---

## Deploying

```bash
helm upgrade --install switchboard-chat ./chart -f chart/values.yaml
```

`install.sh` and `/apply` both run this for you, and automatically layer in
`chart/values-secrets.yaml` if it exists:

```bash
helm upgrade --install switchboard-chat ./chart \
  -f chart/values.yaml \
  -f chart/values-secrets.yaml   # only if present
```

Preview rendered manifests without applying anything:

```bash
helm template ./chart -f chart/values.yaml
```

---

## Secrets

`values.yaml` ships with placeholder dev credentials (`root` / `rootpassword`)
so the chart works out of the box. Never put real credentials there — it's
meant to be committed. Instead:

```bash
cp chart/values-secrets.example.yaml chart/values-secrets.yaml
# edit chart/values-secrets.yaml with real values
```

`chart/values-secrets.yaml` is gitignored. For anything beyond local dev,
replace this pattern with Vault, sealed-secrets, or external-secrets-operator
(see `docs/CONVENTIONS.md`).

---

## Customizing for your own project

Almost everything is a value:

| Want to change | Edit in `values.yaml` |
|---|---|
| Image name/tag | `backend.image.*`, `frontend.image.*` |
| Namespaces | `namespaces.app`, `namespaces.db` |
| Ports, replicas, resources | `backend.*`, `frontend.*`, `mongodb.*` |
| Ingress host / class | `ingress.*` |
| Disable network policies | `networkPolicies.enabled: false` |

Adding a brand-new service is the one thing values.yaml can't do alone — see
`docs/ADDING-A-SERVICE.md` for adding a new `templates/app/<name>/` folder.
