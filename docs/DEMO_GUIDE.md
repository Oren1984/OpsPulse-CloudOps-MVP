# Five-Minute Demo Guide

A scripted walkthrough for an interview or client demo. Total time: ~5 minutes.

## 0. Setup (before the call)

```bash
cp .env.example .env
docker compose up -d --build
```
Wait ~30s, then confirm: `curl -s http://localhost:8080/healthz`.

## 1. Start the healthy system (30s)

Open `http://localhost:8080/` — the dashboard shows seeded services
(all `healthy`) and the sample resolved incident. Mention: one FastAPI
service, PostgreSQL persistence, structured logging, Prometheus metrics —
all container-based, same image runs locally and in Kubernetes.

## 2. Show the Grafana dashboard (30s)

Open `http://localhost:53000` (admin/admin) → **OpsPulse Overview**.
Point out: HTTP request rate, error rate, P95 latency, application health,
PostgreSQL connectivity, open incidents — all live.

## 3. Trigger the controlled demo failure (30s)

```bash
curl -s -X POST http://localhost:8080/api/demo/fail \
  -H "X-API-Key: ${API_KEY:-change-me-demo-key}"
```
Explain: this is a deliberate, reversible fault injector, gated behind
`DEMO_MODE_ENABLED` (off by default in the Helm chart / any real deployment),
and protected by the same `X-API-Key` requirement used by write operations.

## 4. Observe changed metrics and an alert (60s)

Generate a little traffic so the change is visible:
```bash
for i in $(seq 1 10); do curl -s -o /dev/null http://localhost:8080/api/services; done
```
In Grafana: latency and error-rate panels move; **Application Health**
still shows UP (the process is fine — only the readiness/business path is
degraded). In Prometheus (`http://localhost:59090/alerts`), point out
`OpsPulseHighErrorRate` / `OpsPulseHighLatency` pending or firing once
their `for:` window elapses.

## 5. Create/display an incident (30s)

```bash
curl -s http://localhost:8080/api/services | python -m json.tool   # copy a service id
curl -s -X POST http://localhost:8080/api/incidents \
  -H "Content-Type: application/json" \
  -d '{"title":"Elevated errors on opspulse-api","service_id":"<service-id>","severity":"high"}'
```
Refresh the dashboard — the new incident appears in the feed.

## 6. Analyze with the AI Incident Assistant (60s)

```bash
curl -s -X POST http://localhost:8080/api/ai/analyze \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY:-change-me-demo-key}" \
  -d '{
    "alert": {"name": "HighErrorRate", "severity": "critical", "description": "5xx spike on opspulse-api"},
    "metrics": [{"name": "error_rate", "value": 42.0, "unit": "%"}],
    "log_excerpt": "ERROR opspulse-api 503 Simulated demo-failure",
    "deployment": {"service_name": "opspulse-api", "version": "local-dev", "environment": "development"}
  }' | python -m json.tool
```

## 7. Display its structured response (included above)

Point out the `source` field (`fallback` unless `AI_BACKEND=bedrock` and
AWS Bedrock access is configured), the confidence level, and the
`insufficient_evidence_warning` behavior — call out that this is read-only:
no commands are ever executed, no infrastructure is ever changed.

## 8. Restore the service (15s)

```bash
curl -s -X POST http://localhost:8080/api/demo/restore \
  -H "X-API-Key: ${API_KEY:-change-me-demo-key}"
```

## 9. Confirm health and metrics recover (30s)

```bash
curl -s http://localhost:8080/readyz
```
Grafana panels return to baseline over the next couple of scrape intervals.

## 10. Deployment via GitHub Actions (or local simulation) (30s)

If a GitHub remote + configured `DEPLOY_ROLE_ARN` is available: show the
`Deploy` workflow run — OIDC auth, image build/push to ECR tagged with the
commit SHA, `helm upgrade`, rollout wait, smoke test, automatic rollback on
failure.

Otherwise, run the local equivalent to demonstrate the same validated
pipeline stages without live AWS/GitHub access:
```bash
make lint && make test && make docker-build && make scan
make helm-lint && make helm-template
make tf-fmt && make tf-validate
```
