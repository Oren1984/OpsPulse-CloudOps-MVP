from unittest.mock import MagicMock, patch

from opspulse.ai.fallback import analyze_fallback
from opspulse.ai.mock import analyze_mock
from opspulse.ai.sanitize import sanitize_text
from opspulse.ai.service import analyze_incident
from opspulse.schemas import AlertContext, DeploymentContext, IncidentAnalysisRequest, MetricSample

SAMPLE_REQUEST = IncidentAnalysisRequest(
    alert=AlertContext(name="HighErrorRate", severity="critical", description="5xx spike"),
    metrics=[MetricSample(name="error_rate", value=12.5, unit="%")],
    log_excerpt="2026-09-10 ERROR opspulse-api 500 Internal Server Error",
    deployment=DeploymentContext(service_name="opspulse-api", version="abc123", environment="development"),
)


def test_sanitize_redacts_secrets_and_truncates():
    dirty = "password=supersecret token: abc.def.ghi AKIAABCDEFGHIJKLMNOP rest of the log"
    cleaned = sanitize_text(dirty, max_chars=1000)
    assert "supersecret" not in cleaned
    assert "AKIAABCDEFGHIJKLMNOP" not in cleaned
    assert "[REDACTED]" in cleaned

    truncated = sanitize_text("x" * 5000, max_chars=100)
    assert len(truncated) == 100


def test_mock_backend_self_identifies():
    result = analyze_mock(SAMPLE_REQUEST)
    assert result.source == "mock"
    assert result.confidence in {"low", "medium", "high"}


def test_fallback_backend_self_identifies_and_flags_low_confidence():
    minimal_request = IncidentAnalysisRequest(
        alert=AlertContext(name="Unknown"),
        deployment=DeploymentContext(service_name="opspulse-api"),
    )
    result = analyze_fallback(minimal_request)
    assert result.source == "fallback"
    assert result.confidence == "low"
    assert result.insufficient_evidence_warning is not None


def test_fallback_error_rate_case_has_evidence():
    result = analyze_fallback(SAMPLE_REQUEST)
    assert result.source == "fallback"
    assert len(result.supporting_evidence) >= 2
    assert 2 <= len(result.recommended_actions) <= 3


@patch("opspulse.config.settings.ai_backend", "mock")
def test_service_dispatches_to_mock_backend():
    result = analyze_incident(SAMPLE_REQUEST)
    assert result.source == "mock"


@patch("opspulse.config.settings.ai_backend", "bedrock")
def test_service_falls_back_when_bedrock_errors():
    with patch("opspulse.ai.bedrock.analyze_bedrock", side_effect=RuntimeError("no aws access")):
        result = analyze_incident(SAMPLE_REQUEST)
    assert result.source == "fallback"


@patch("opspulse.config.settings.ai_backend", "bedrock")
def test_service_uses_bedrock_when_mocked_success():
    fake_bedrock_response = MagicMock()
    fake_bedrock_response.source = "bedrock"
    with patch("opspulse.ai.bedrock.analyze_bedrock", return_value=fake_bedrock_response) as mocked:
        result = analyze_incident(SAMPLE_REQUEST)
    mocked.assert_called_once()
    assert result.source == "bedrock"


async def test_ai_analyze_endpoint_returns_structured_response(client):
    resp = await client.post(
        "/api/ai/analyze",
        json={
            "alert": {"name": "HighLatency", "severity": "warning", "description": "p95 above SLO"},
            "metrics": [{"name": "p95_latency_ms", "value": 950, "unit": "ms"}],
            "log_excerpt": "slow query on incidents table",
            "deployment": {"service_name": "opspulse-api", "version": "abc123", "environment": "development"},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["source"] in {"mock", "fallback", "bedrock"}
    assert "summary" in body
    assert "recommended_actions" in body
