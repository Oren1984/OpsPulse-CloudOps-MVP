#!/usr/bin/env bash
# Smoke test against a running OpsPulse instance (local compose or a
# port-forwarded Kubernetes service). Exits non-zero on any failure.
set -euo pipefail

BASE_URL="${1:-http://localhost:${APP_HOST_PORT:-8080}}"

check() {
  local path="$1"
  local expected="$2"
  local code
  code=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${path}")
  if [ "$code" != "$expected" ]; then
    echo "FAIL: ${path} returned ${code}, expected ${expected}"
    exit 1
  fi
  echo "OK: ${path} -> ${code}"
}

echo "Smoke testing ${BASE_URL}"
check "/healthz" 200
check "/readyz" 200
check "/metrics" 200
check "/api/services" 200
check "/api/incidents" 200

echo "All smoke checks passed."
