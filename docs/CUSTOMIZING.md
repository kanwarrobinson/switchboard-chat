# Customizing This Base Project

This project is meant to be forked. There are two ways to start, depending
on how you got here — pick one, then follow steps 2 onward either way.

---

## 1a. Generate a new project into its own folder (recommended)

Clone this base repo somewhere you'll keep it as a reusable source, then run:

```bash
./scripts/create-project.sh
```

It asks where to create the new project and what to call it, copies the
reusable platform pieces (`install.sh`, `uninstall.sh`, `kind-config.yaml`,
`chart/`, `docs/`, `.claude/`, `.github/`) plus the placeholder
`src/backend`/`src/frontend` sample into that new location, and rewrites
every reference to `switchboard-chat` → `<your-project-name>` and
`switchboard-chat-cluster` → `<your-project-name>-cluster` throughout the copy. This
base repo itself is left untouched — run it again anytime to stamp out
another project.

The result is plain files, no git repo — run `git init` yourself once you're
in the new folder. It does **not** touch credentials (that's step 3).

## 1b. Rename this checkout in place

If instead you cloned this base directly into your project's final home and
just want it renamed — no separate copy — run:

```bash
./scripts/bootstrap-new-project.sh <your-project-name>
```

This rewrites the same references as above, but in place, in the current
checkout. Review the diff (`git diff`) before committing. Safe to run again
later if you rename the project a second time.

Neither script touches `src/backend` or `src/frontend` (that's step 2).

---

## 2. Replace the placeholder services

`src/backend` and `src/frontend` exist only to prove the platform works end
to end — ingress routes to both, the backend talks to MongoDB, health probes
pass. They are not meant to survive into a real project.

- Keep: the `Dockerfile`'s exposed port, and a `GET /health` endpoint
  returning `200` — the chart's liveness/readiness probes and ingress rules
  depend on both.
- Replace: everything else. See `src/backend/README.md` and
  `src/frontend/README.md` for exactly what's swappable.

If you rename the services themselves (not just the project), update
`chart/values.yaml` (`backend.name`/`frontend.name`, image repository) and
the matching `chart/templates/app/<service>/` files — see
`docs/ADDING-A-SERVICE.md`.

---

## 3. Set real secrets

`chart/values.yaml` ships placeholder MongoDB and API credentials
(`root` / `rootpassword`, `changeme`) so the chart deploys out of the box.
**Never edit real credentials into that file** — it's meant to be committed.

```bash
cp chart/values-secrets.example.yaml chart/values-secrets.yaml
# edit chart/values-secrets.yaml with real values
```

`chart/values-secrets.yaml` is gitignored. `install.sh` and `/apply` both
pick it up automatically if it exists. Beyond local dev, replace this
pattern entirely with Vault, sealed-secrets, or external-secrets-operator —
see `docs/CONVENTIONS.md`.

---

## 4. Adjust sizing and networking

Everything else lives in `chart/values.yaml`:

| Want to change | Where |
|---|---|
| Image repository/tag | `backend.image.*`, `frontend.image.*` |
| Namespace names | `namespaces.app`, `namespaces.db` |
| Ports, replica counts | `backend.port`/`replicas`, `frontend.port`/`replicas` |
| Resource requests/limits | `backend.resources`, `frontend.resources`, `mongodb.resources` |
| Ingress class / hostname | `ingress.className`, `ingress.host` |
| Disable network policies (debugging) | `networkPolicies.enabled: false` |

Run `/apply` (or `helm upgrade --install ...`, see `chart/README.md`) after
any change.

---

## 5. Add your own services

See `docs/ADDING-A-SERVICE.md` — either run `/add-service <name>` or follow
the manual steps to add a new `chart/templates/app/<name>/` folder and
register it in `chart/values.yaml`.

---

## What this base project does *not* solve

Tracked in `ROADMAP.md`:

- **CI/CD beyond image builds** (Phase 3) — `.github/workflows/ci.yml` builds
  and lints; wiring it to push to a registry and deploy is project-specific.
- **Observability** (Phase 4) — no metrics/logging stack included.
- **Production hardening** (Phase 5) — no TLS, secrets manager, HPA, backups,
  or RBAC beyond namespace isolation. This is a local dev/staging base, not a
  production deployment target as-is.
