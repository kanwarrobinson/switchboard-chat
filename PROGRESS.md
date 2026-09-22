# Project Progress

> Update this file as tasks are completed. Claude reads this at the start of every session.

---

## ✅ Done

- [x] Project structure defined
- [x] Prerequisites verified (Docker, kind, kubectl, helm)
- [x] All 49 files generated (CLAUDE.md, manifests, src, docs, commands)
- [x] Converted raw `k8s/` manifests to a parametrized Helm chart (`chart/`) —
      `install.sh`/`uninstall.sh`/`/apply` now deploy via `helm upgrade --install`
- [x] Separated real secrets from committed values (`chart/values-secrets.example.yaml` → gitignored `chart/values-secrets.yaml`)
- [x] Added `scripts/bootstrap-new-project.sh` to rename the project/cluster identity on fork — tested against a scratch copy
- [x] Added `scripts/create-project.sh` — interactive generator that copies this base into a new target folder + renames it there, so the base repo can be cloned once and reused to stamp out multiple projects; rename logic factored into `scripts/lib/rename.sh` shared by both scripts. Tested: happy path, non-empty-target guard, invalid-name guard, and post-generation `helm lint`/`helm template` on the output.
- [x] `create-project.sh` no longer copies the `scripts/` folder (bootstrap-new-project.sh + lib/) into generated projects — not needed once a project is created, per user feedback
- [x] `install.sh` now checks for host port conflicts (another kind cluster already bound to 80/443) before creating the cluster, and prompts to delete the conflicting one (`--yes` to auto-confirm) — tested against a real decoy cluster
- [x] Added root `README.md` (human-facing), `LICENSE` (MIT placeholder), `.gitignore`
- [x] Added `docs/CUSTOMIZING.md` — step-by-step guide for turning this into a real project
- [x] Added starter CI (`.github/workflows/ci.yml`) — builds both images, `helm lint`/`helm template`, backend test/lint
- [x] Marked `src/backend` and `src/frontend` as placeholder/example code in their READMEs and in CLAUDE.md/AGENTS.md

---

## 🔄 In Progress

- [ ] Run `install.sh` against the new Helm-based flow to confirm a clean first install
- [ ] Verify all pods come up healthy

---

## 📌 Pending

- [ ] Replace placeholder backend `index.js` with real application code
- [ ] Replace placeholder frontend `index.html` with real UI
- [ ] Test network policies are enforcing correctly
- [ ] Verify MongoDB StatefulSet PVC binds correctly
- [ ] Test ingress routing (/ → frontend, /api → backend)
- [ ] Add resource limits tuning after observing real usage
- [ ] Set up Phase 2 — real application code
- [ ] `git init` this repo (deliberately left undone — see chat history)
- [ ] Wire CI to actually push images / deploy somewhere (Phase 3, project-specific)

---

## 🐛 Known Issues

_None yet — will be tracked here as they surface._

---

## 📝 Notes

- Cluster name: `switchboard-chat-cluster`
- MongoDB credentials are placeholder (`root` / `rootpassword`) — change before any real use
- `imagePullPolicy: Never` is set on backend and frontend — always run `kind load docker-image` after rebuilding
