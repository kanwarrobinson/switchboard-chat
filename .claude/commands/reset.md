# /reset

Tears down the kind cluster completely and recreates it from scratch.

## Usage

```
/reset
```

## Steps

1. Confirm with the user before proceeding — this is destructive
2. Run `kind delete cluster --name switchboard-chat-cluster` (this also wipes the Helm release — no need to `helm uninstall` first)
3. Run `./install.sh` to recreate everything

## Warning

- All data in MongoDB PVC will be lost
- All pods and services will be deleted
- The kind cluster itself is deleted
- Always confirm before running

## When to use

- When the cluster is in a broken state
- When you want a completely clean slate
- After major changes to `kind-config.yaml`
