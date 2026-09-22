# /logs

Tails logs for a service pod.

## Usage

```
/logs backend
/logs frontend
/logs mongodb
```

## Commands

For backend or frontend (namespace: app):
```bash
kubectl logs -f deployment/<service> -n app --tail=50
```

For mongodb (namespace: db):
```bash
kubectl logs -f statefulset/mongodb -n db --tail=50
```

## Notes

- If the pod has multiple containers, specify `-c <container-name>`
- For previous container logs (after crash): add `--previous`
- For all pods matching a label: `kubectl logs -l app=<service> -n <ns>`
