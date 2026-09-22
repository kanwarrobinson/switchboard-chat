# /apply

Deploys or updates the Helm release for this project.

## Usage

```
/apply
/apply --dry-run
```

## What it does

```bash
value_files=(-f chart/values.yaml)
[[ -f chart/values-secrets.yaml ]] && value_files+=(-f chart/values-secrets.yaml)

helm upgrade --install switchboard-chat ./chart "${value_files[@]}" --wait --timeout=180s
```

Add `--dry-run` to preview the diff-equivalent without applying:

```bash
helm upgrade --install switchboard-chat ./chart "${value_files[@]}" --dry-run --debug
```

## Notes

- Idempotent — safe to re-run any time `chart/values.yaml`, templates, or images change.
- `helm template ./chart -f chart/values.yaml` renders manifests without touching the cluster.
- `chart/values-secrets.yaml` (gitignored) is layered in automatically when present — see `chart/README.md`.
- This is what `install.sh` runs internally; `/apply` is for re-deploying after you've already run `./install.sh` once.
