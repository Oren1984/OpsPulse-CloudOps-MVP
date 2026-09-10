# Operations Runbook

POC/MVP runbook. Not a production incident-response document.

## Start / stop

**Local (Docker Compose):**
```bash
cp .env.example .env   # first time only
docker compose up -d --build
docker compose down     # add -v to also drop data volumes
```

**Kubernetes (Helm):**
```bash
helm upgrade --install opspulse helm/opspulse -n opspulse --create-namespace \
  --set image.repository=<ecr-url> --set image.tag=<sha> \
  --set database.host=<rds-endpoint>
```

## Health verification

```bash
curl -s http://localhost:8080/healthz   # liveness — process is up
curl -s http://localhost:8080/readyz    # readiness — DB reachable, not degraded
curl -s http://localhost:8080/metrics | head -30
bash scripts/smoke_test.sh              # full smoke check
```

In Kubernetes: `kubectl get pods -n opspulse`, `kubectl describe pod <pod> -n opspulse`.

## Common failure diagnosis

| Symptom | Likely cause | Check |
|---|---|---|
| `/readyz` returns 503, `database: false` | Postgres unreachable | `docker compose logs postgres`, or in K8s: RDS security group / `DB_HOST` ConfigMap value |
| `/readyz` returns 503, `database: true` | Demo failure is active | `curl -s http://localhost:8080/api/demo/status`, then `POST /api/demo/restore` |
| App container won't start | Migration failure | `docker compose logs app` — `alembic upgrade head` runs before `uvicorn` and will fail loudly on a bad migration |
| High error rate / high latency alert firing | Real regression, or the demo failure is active | Check `opspulse_demo_failure_active` in Prometheus/Grafana first |
| Pod restarting repeatedly (K8s) | Liveness probe failing, OOMKilled, or crash on startup | `kubectl describe pod`, `kubectl logs --previous` |

## Monitoring and alert inspection

- Prometheus UI: `http://localhost:59090` → **Alerts** tab, or **Graph**
  with a query like `opspulse_http_requests_total`.
- Grafana: `http://localhost:53000` (admin/admin by default) → **OpsPulse
  Overview** dashboard (auto-provisioned).
- Alert rules live in `monitoring/prometheus/alert_rules.yml`: high error
  rate, high latency, application unavailable, PostgreSQL unavailable,
  repeated pod restarts (Kubernetes only — requires kube-state-metrics).

## Rollback procedure

**Helm:**
```bash
helm history opspulse -n opspulse
helm rollback opspulse <previous-revision> -n opspulse --wait --timeout 5m
```
The `deploy.yml` GitHub Actions workflow does this automatically if rollout
or the post-deploy smoke test fails.

**Local Docker Compose:** re-run `docker compose up -d --build` after
checking out the previous known-good commit — there is no separate
rollback mechanism for the local stack.

## Database checks

```bash
docker compose exec postgres psql -U opspulse -d opspulse -c "\dt"
docker compose exec postgres psql -U opspulse -d opspulse -c "SELECT count(*) FROM services;"
cd app && DATABASE_URL=postgresql+psycopg2://opspulse:opspulse@localhost:55432/opspulse alembic current
```

## AWS cleanup

```bash
cd terraform
terraform destroy
```
Verify in the AWS console (or `aws eks list-clusters`, `aws rds
describe-db-instances`, `aws ecr describe-repositories`) that no OpsPulse
resources remain, since this POC intentionally does not enable deletion
protection or final snapshots.

## Controlled-failure recovery

1. Trigger: `curl -s -X POST http://localhost:8080/api/demo/fail` (only
   works when `DEMO_MODE_ENABLED=true`).
2. Observe: `/readyz` returns 503; `GET /api/services` gets ~1.2s slower
   and returns 503 on roughly 60% of calls; Prometheus/Grafana show the
   error rate and latency panels move, and the `OpsPulseHighErrorRate` /
   `OpsPulseHighLatency` alerts should fire after their `for:` window.
3. Restore: `curl -s -X POST http://localhost:8080/api/demo/restore`.
4. Confirm: `/readyz` returns 200 again; metrics return to baseline within
   the next scrape interval; alerts resolve after their evaluation window.
