#!/usr/bin/env bash
# Smoke test against a running OpsPulse instance (local compose or a
# port-forwarded Kubernetes service). Exits non-zero on any failure.
set -euo pipefail

BASE_URL="${1:-http://localhost:${APP_HOST_PORT:-8080}}"
API_KEY="${API_KEY:-change-me-demo-key}"

check() {
  local path="$1"
  local expected="$2"
  local auth_header="${3:-}"
  local code
  local curl_cmd=(curl -s -o /dev/null -w "%{http_code}")
  if [ -n "$auth_header" ]; then
    curl_cmd+=( -H "X-API-Key: ${auth_header}" )
  fi
  curl_cmd+=("${BASE_URL}${path}")
  code=$("${curl_cmd[@]}")
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
check "/api/services" 200 "$API_KEY"
check "/api/incidents" 200 "$API_KEY"

echo "All smoke checks passed."
