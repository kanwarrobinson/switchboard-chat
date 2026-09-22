# /release

Full rebuild and deploy pipeline — builds both images, loads them, and restarts all app pods.

## Usage

```
/release
/release backend
/release frontend
```

## Steps (full release)

1. `docker build -t backend:local ./src/backend`
2. `docker build -t frontend:local ./src/frontend`
3. `kind load docker-image backend:local --name switchboard-chat-cluster`
4. `kind load docker-image frontend:local --name switchboard-chat-cluster`
5. `kubectl rollout restart deployment/backend -n app`
6. `kubectl rollout restart deployment/frontend -n app`
7. `kubectl rollout status deployment/backend -n app`
8. `kubectl rollout status deployment/frontend -n app`
9. Show final pod status

## Steps (single service)

If `$ARGUMENTS` is `backend` or `frontend`, only rebuild and restart that service.

## Notes

- MongoDB is not rebuilt (it uses the official `mongo:7.0` image)
- After release, verify with `/status`
- If something breaks, check with `/debug <service>`
