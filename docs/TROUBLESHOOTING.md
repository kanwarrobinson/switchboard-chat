# Troubleshooting

---

## Pod Issues

### `ImagePullBackOff` or `ErrImageNeverPull`

**Cause**: Image not loaded into the kind node.

**Fix**:
```bash
# Check if image is in kind node
docker exec -it switchboard-chat-cluster-control-plane crictl images | grep <service>

# If missing, reload
kind load docker-image <service>:local --name switchboard-chat-cluster
kubectl rollout restart deployment/<service> -n app
```

---

### `CrashLoopBackOff`

**Cause**: Application is crashing on startup.

**Fix**:
```bash
# Get logs from current container
kubectl logs deployment/<service> -n app --tail=50

# Get logs from previous (crashed) container
kubectl logs deployment/<service> -n app --previous --tail=50

# Describe pod for events
kubectl describe pod -n app -l app=<service>
```

Common causes:
- Missing environment variable (check ConfigMap and Secret)
- MongoDB connection failing (check MONGO_URI in secret)
- App code error (check `src/<service>/index.js`)

---

### Pod stuck in `Pending`

**Cause**: Usually PVC not binding or no schedulable nodes.

**Fix**:
```bash
kubectl describe pod -n <ns> <pod-name>
# Look at Events section at the bottom

# For PVC issues
kubectl get pvc -n db
kubectl describe pvc -n db
```

---

## MongoDB Issues

### MongoDB pod not starting

```bash
kubectl describe statefulset/mongodb -n db
kubectl logs statefulset/mongodb -n db --tail=50
kubectl get pvc -n db
```

### Backend can't connect to MongoDB

```bash
# Check the MONGO_URI in backend secret
kubectl get secret backend-secret -n app -o jsonpath='{.data.MONGO_URI}' | base64 -d

# Test DNS resolution from backend pod
kubectl exec deployment/backend -n app -- nslookup mongodb-0.mongodb.db.svc.cluster.local

# Test TCP connectivity
kubectl exec deployment/backend -n app -- nc -zv mongodb-0.mongodb.db.svc.cluster.local 27017
```

---

## Network Policy Issues

### Traffic being blocked unexpectedly

```bash
# Check what policies exist
kubectl get networkpolicy --all-namespaces

# Temporarily delete deny-all to test (dev only!)
kubectl delete networkpolicy deny-all -n app

# Test connectivity
kubectl run test --image=busybox --rm -it --restart=Never -n app \
  -- wget -qO- http://backend:3000/health

# Re-apply everything from the chart (recreates deny-all along with the rest)
/apply
```

### Calico not enforcing policies

```bash
# Verify Calico is running
kubectl get pods -n kube-system | grep calico

# If not running, reinstall
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml
```

---

## Ingress Issues

### `http://localhost` not responding

```bash
# Check ingress controller is running
kubectl get pods -n ingress-nginx

# Check ingress resource
kubectl get ingress -n app
kubectl describe ingress app-ingress -n app

# Check port mapping on kind node
docker ps | grep switchboard-chat-cluster
# Should show 0.0.0.0:80->80/tcp
```

### 404 from nginx

- Check path rules in `chart/templates/ingress.yaml`
- Make sure backend/frontend services are running
- Check `kubectl get svc -n app`

---

## Kind Cluster Issues

### `Bind for 0.0.0.0:80 failed: port is already allocated`

**Cause**: Another kind cluster (often an older one from a previous
project/run) is already bound to host port 80/443. Only one kind cluster on
the machine can hold those ports at a time.

**Fix**: `install.sh` detects this itself now — before creating the cluster
it checks for a conflicting container and, if found, asks:

```
Delete kind cluster '<other-cluster>' to free the port and continue? (y/N):
```

Answer `y` to have it delete the other cluster and proceed, or `N` to abort
and resolve it yourself (delete it manually, or change the `hostPort` values
in `kind-config.yaml` to run both side by side). Pass `./install.sh --yes` to
auto-confirm without prompting (e.g. in CI).

### Cluster not starting

```bash
# Delete and recreate
kind delete cluster --name switchboard-chat-cluster
./install.sh
```

### kubectl pointing to wrong cluster

```bash
kubectl config use-context kind-switchboard-chat-cluster
kubectl config current-context
```

---

## Helm Issues

### nginx ingress install fails

```bash
helm repo update
helm delete ingress-nginx -n ingress-nginx 2>/dev/null || true
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.service.type=NodePort \
  --set controller.hostPort.enabled=true \
  --wait
```

---

## Quick Diagnostic Checklist

```bash
# 1. Is the cluster running?
kind get clusters

# 2. Is kubectl pointed at the right cluster?
kubectl config current-context

# 3. Are all pods running?
kubectl get pods --all-namespaces

# 4. Are services correct?
kubectl get svc -n app
kubectl get svc -n db

# 5. Is ingress routing?
kubectl get ingress -n app

# 6. Any recent events?
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | tail -20
```
