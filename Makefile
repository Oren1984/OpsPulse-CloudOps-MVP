.PHONY: up down logs seed test lint docker-build helm-lint helm-template tf-fmt tf-validate scan smoke demo-fail demo-restore

## Local stack (Docker Compose)
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

seed:
	docker compose run --rm seed

## Application
test:
	cd app && python -m pytest -v

lint:
	cd app && ruff check .

docker-build:
	docker build -t opspulse:local -f app/Dockerfile app

scan:
	trivy image --severity HIGH,CRITICAL opspulse:local

## Kubernetes / Helm
helm-lint:
	helm lint helm/opspulse

helm-template:
	helm template opspulse helm/opspulse \
		--set image.repository=example/opspulse \
		--set image.tag=local \
		--set database.host=example.rds.amazonaws.com

## Terraform
tf-fmt:
	cd terraform && terraform fmt -check -recursive

tf-validate:
	cd terraform && terraform init -backend=false && terraform validate

## Demo
smoke:
	bash scripts/smoke_test.sh

demo-fail:
	curl -s -X POST http://localhost:$${APP_HOST_PORT:-8080}/api/demo/fail

demo-restore:
	curl -s -X POST http://localhost:$${APP_HOST_PORT:-8080}/api/demo/restore
