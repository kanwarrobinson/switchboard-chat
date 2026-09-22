# /debug

Diagnoses issues with a pod or service.

## Usage

```
/debug backend
/debug frontend
/debug mongodb
```

## Diagnostic steps to run

### 1. Check pod status
```bash
kubectl get pods -n <namespace> -l app=<service>
```

### 2. Describe the pod (shows events, image pull errors, scheduling issues)
```bash
kubectl describe pod -n <namespace> -l app=<service>
```

### 3. Check logs
```bash
kubectl logs -n <namespace> -l app=<service> --tail=50
kubectl logs -n <namespace> -l app=<service> --previous --tail=50
```

### 4. Check if image is loaded in kind
```bash
docker exec -it switchboard-chat-cluster-control-plane crictl images | grep <service>
```

### 5. Check network policy (is traffic blocked?)
```bash
kubectl get networkpolicy -n <namespace>
kubectl describe networkpolicy -n <namespace>
```

### 5b. Check what Helm actually rendered/applied
```bash
helm get manifest switchboard-chat | grep -A 20 "kind: Deployment" | grep -A 20 "name: <service>"
```

### 6. Test connectivity from a debug pod
```bash
kubectl run debug --image=busybox --rm -it --restart=Never -n app -- wget -qO- http://<service>:<port>/health
```

## Namespace lookup

| Service | Namespace |
|---------|-----------|
| backend | app |
| frontend | app |
| mongodb | db |

## Common issues

| Symptom | Likely cause |
|---------|-------------|
| `ImagePullBackOff` | Image not loaded with `kind load docker-image` |
| `CrashLoopBackOff` | App is crashing — check logs |
| `Pending` | PVC not bound or no resources |
| Connection refused | Network policy blocking or wrong port |
| `ErrImageNeverPull` | `imagePullPolicy: Never` but image not in node |
