# /status

Shows the current state of the cluster — pods, services, and ingress across all namespaces.

## Usage

```
/status
```

## Commands to run

```bash
echo "=== Cluster ==="
kubectl cluster-info --context kind-switchboard-chat-cluster

echo "\n=== Helm release ==="
helm status switchboard-chat 2>/dev/null || echo "  (release not found)"

echo "\n=== Namespace: app ==="
kubectl get pods,svc -n app -o wide

echo "\n=== Namespace: db ==="
kubectl get pods,svc -n db -o wide

echo "\n=== Ingress ==="
kubectl get ingress -n app

echo "\n=== Network Policies ==="
kubectl get networkpolicy -n app
kubectl get networkpolicy -n db

echo "\n=== Events (last 10) ==="
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -10
```

## Notes

- Pods in `Pending` state usually mean image not loaded or PVC not bound
- Pods in `CrashLoopBackOff` — run `/logs <service>` to investigate
- `ImagePullBackOff` means `imagePullPolicy: Never` is missing or image wasn't loaded with `kind load`
