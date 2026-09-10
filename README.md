# OpsPulse MVP

OpsPulse is a small cloud-ops demo app built as a POC / MVP for service monitoring, incident tracking, and a simple AI-assisted ops workflow.

## What this demo shows

- Service inventory and health overview
- Incident creation and tracking
- Demo failure / recovery flow
- Metrics and dashboard visibility
- Lightweight AI assistant behavior for operational triage

## Fast local run

```bash
docker compose up -d --build
```

Open:

- App: http://localhost:8080/
- API docs: http://localhost:8080/docs
- Prometheus: http://localhost:59090
- Grafana: http://localhost:53000

Stop:

```bash
docker compose down
```

## Notes

- This is a demo project, not a production platform.
- Mutating routes require an `X-API-Key` header.
- The demo failure flow is intentional and for presentation use only.

## Repo structure

```text
app/         FastAPI app, tests, Docker setup
helm/        Helm packaging
terraform/   IaC examples
monitoring/  Prometheus and Grafana config
docs/        Architecture, runbook, and demo notes
```

## Quick validation

```bash
cd app
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements-dev.txt
pytest -q
```

This is meant to be a short, understandable MVP that shows real engineering patterns without turning into a large enterprise system.
