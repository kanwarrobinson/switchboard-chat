# /rebuild

Rebuilds a service image, loads it into the kind cluster, and restarts the deployment.

## Usage

```
/rebuild backend
/rebuild frontend
/rebuild all
```

## Steps

1. Run `docker build -t <service>:local ./src/<service>`
2. Run `kind load docker-image <service>:local --name switchboard-chat-cluster`
3. Run `kubectl rollout restart deployment/<service> -n app`
4. Run `kubectl rollout status deployment/<service> -n app` to confirm

## Notes

- Always use `imagePullPolicy: Never` — the image must be loaded via `kind load`
- After rebuild, wait for the rollout to complete before testing
- If `$ARGUMENTS` is `all`, rebuild both backend and frontend
