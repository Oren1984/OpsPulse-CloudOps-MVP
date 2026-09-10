# OpsPulse

OpsPulse is a compact cloud-ops MVP for monitoring service health, tracking incidents, and showing how a small DevSecOps workflow can be packaged into a credible demo. It combines a FastAPI app, PostgreSQL persistence, Prometheus metrics, Grafana dashboards, Kubernetes packaging, and an AI-assisted incident flow.

## What it demonstrates

- Service inventory and incident tracking in a single app
- Live metrics collection and dashboarding
- Controlled fail/recovery demo behavior for presentations
- AI incident assistant with Bedrock, mock, and fallback modes
- Local Docker workflow plus Helm and AWS IaC validation paths

## Local quick start

```bash
cp .env.example .env
docker compose up -d --build
```

Open the stack locally:

- App: http://localhost:8080/
- API docs: http://localhost:8080/docs
- Prometheus: http://localhost:59090
- Grafana: http://localhost:53000 (admin / admin)

Stop it with:

```bash
docker compose down
```

## Security and demo controls

- Mutable routes require an `X-API-Key` header and fail closed when the key is missing or incorrect.
- The demo-failure mechanism is intentionally gated and meant only for presentation flow.
- AWS infrastructure is represented in Terraform and checked with validation-only workflows in this repo; no live AWS resources were created here.

## Repository layout

```text
app/             FastAPI app, tests, Alembic migrations, Dockerfile
helm/opspulse/   Helm deployment for Kubernetes packaging
terraform/       AWS IaC modules and IAM/OIDC trust configuration
monitoring/      Prometheus and Grafana provisioning
scripts/         Smoke tests and operational helpers
docs/            Architecture, runbook, and demo guide
```

## Validation

```bash
cd app
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements-dev.txt
pytest -q
ruff check .
```

## Five-minute demo flow

1. Start the stack.
2. Open the dashboard and confirm the service view.
3. Trigger the demo failure and watch the app respond.
4. Review or create an incident.
5. Run the AI assistant and restore the healthy state.

See [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md) for the presentation script.

## Documentation

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/OPERATIONS_RUNBOOK.md](docs/OPERATIONS_RUNBOOK.md)
- [docs/DEMO_GUIDE.md](docs/DEMO_GUIDE.md)

This is a portfolio MVP, not a production system. It is intentionally small, clear, and easy to understand while still showing real engineering patterns around monitoring, deployment readiness, and AI-assisted operations.
