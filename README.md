# switchboard-chat

A **base project** for shipping a small app on Kubernetes: Node.js backend +
static frontend + MongoDB, running locally on [kind](https://kind.sigs.k8s.io/),
deployed with Helm, with namespace isolation, default-deny network policies,
and nginx ingress already wired up.

Clone it, replace the two placeholder services with your real app, and you
have a working local Kubernetes environment — namespaces, network policies,
ingress, health probes, and a Helm chart — without building any of that
plumbing yourself.

---

## Is this for you?

Use this if you want a **local kind cluster with a real production-shaped
topology** (isolated namespaces, default-deny network policies, ingress
routing, a stateful database) to build an app on top of, without setting all
of that up from scratch.

It is not a hosted platform, a scaffolding CLI, or a production deployment
target — Phase 5 in [ROADMAP.md](ROADMAP.md) tracks what's still missing for
that (TLS, secrets management, HPA, backups, RBAC).

---

## What you get

- A **kind cluster** with Calico CNI (so `NetworkPolicy` actually enforces) and nginx ingress
- **Namespace isolation** — `app` (frontend, backend) and `db` (MongoDB), default-deny between them
- A **Helm chart** (`chart/`) — the single place you edit to change image names, ports, replica counts, resource limits, or hostnames
- **Placeholder services** in `src/backend` and `src/frontend` that prove the whole path works end to end (ingress → frontend/backend → MongoDB) — delete and replace them with your app
- **Slash commands** for Claude Code / Codex (`/rebuild`, `/apply`, `/status`, `/debug`, `/add-service`, …) that already know this project's shape
- **Docs** covering conventions, network policy rules, troubleshooting, and how to add a new service

---

## Quick start — try this base project as-is

```bash
git clone <this-repo> && cd switchboard-chat
./install.sh
```

Requires Docker, [kind](https://kind.sigs.k8s.io/), `kubectl`, and `helm`.
`install.sh` checks for all four and tells you what's missing.

Once it finishes:

- **http://localhost/** → frontend
- **http://localhost/api** → backend API
- **http://localhost/health** → backend health check

Tear down (keeps the kind cluster, removes the app) with `./uninstall.sh`, or
wipe everything with `/reset`.

---

## Starting your own project on top of this

Clone this repo once, then generate a fresh, independent project from it —
as many times as you like, into wherever you want:

```bash
./scripts/create-project.sh
```

It asks two questions — where to create the new project, and what to call
it — then copies the reusable platform pieces (install/uninstall scripts,
Helm chart, docs, Claude Code commands, CI, and the placeholder backend/
frontend sample) into that location and renames the cluster/chart identity
throughout. This base repo itself is left untouched.

The generated project is plain files — no `git init` is done for you. From there:

1. **Replace the placeholder services.** `src/backend` and `src/frontend`
   exist only to prove the platform works — swap in your real app, keeping
   the `Dockerfile`'s port and the `GET /health` endpoint (the chart's probes
   and ingress rules depend on both). See each service's `README.md`.
2. **Set real secrets.** `chart/values.yaml` ships placeholder MongoDB/API
   credentials so the chart works out of the box — never put real ones
   there. Copy `chart/values-secrets.example.yaml` to `chart/values-secrets.yaml`
   (gitignored) instead. See `chart/README.md`.
3. **Adjust what needs adjusting** in `chart/values.yaml` — ports, replicas,
   resource requests/limits, ingress hostname — everything else follows.

Already cloned this base directly into your project's final home instead,
and just want it renamed in place (no copy to a new folder)? Use
`./scripts/bootstrap-new-project.sh <name>` instead — see
[docs/CUSTOMIZING.md](docs/CUSTOMIZING.md) for both paths in detail.

---

## Project layout

See [CLAUDE.md](CLAUDE.md) (or [AGENTS.md](AGENTS.md)) for the full layout
and the assistant-facing operating instructions. Key docs:

| Doc | What it covers |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Full system architecture |
| [docs/CONVENTIONS.md](docs/CONVENTIONS.md) | Naming, labeling, port rules |
| [docs/NETWORK-POLICIES.md](docs/NETWORK-POLICIES.md) | Network topology and policy rules |
| [docs/ADDING-A-SERVICE.md](docs/ADDING-A-SERVICE.md) | How to add a new microservice |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common issues and fixes |
| [docs/CUSTOMIZING.md](docs/CUSTOMIZING.md) | Turning this base into your own project |
| [chart/README.md](chart/README.md) | Helm chart structure and values |
| [ROADMAP.md](ROADMAP.md) | Phases — where CI/CD, observability, and hardening land |
| [PROGRESS.md](PROGRESS.md) | Current task tracking |

---

## License

[MIT](LICENSE) — a placeholder so this is usable as a template; update the
copyright line for your own project.
