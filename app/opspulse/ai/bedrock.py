"""Amazon Bedrock backend for the AI Incident Assistant.

Read-only text analysis only: this module never executes commands,
never changes infrastructure, and never transmits credentials or secrets.
The incident context is sanitized and size-bounded before it reaches
this module (see opspulse.ai.sanitize and IncidentAnalysisRequest).
"""

import json

from opspulse.config import settings
from opspulse.logging_config import get_logger
from opspulse.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse

logger = get_logger("opspulse.ai.bedrock")

_PROMPT_TEMPLATE = """You are an SRE incident-analysis assistant. You perform \
READ-ONLY analysis. You do not execute commands or change infrastructure.

Analyze the following bounded incident context and respond with ONLY a JSON \
object with keys: summary, likely_cause, supporting_evidence (array of strings), \
recommended_actions (array of 2-3 strings), confidence ("low"|"medium"|"high"), \
insufficient_evidence_warning (string or null).

Incident context:
Alert: {alert_name} (severity: {alert_severity})
Alert description: {alert_description}
Deployment: service={service_name} version={version} environment={environment}
Metrics: {metrics}
Log excerpt (sanitized, truncated): {log_excerpt}
"""


def _build_prompt(request: IncidentAnalysisRequest) -> str:
    metrics_str = ", ".join(f"{m.name}={m.value}{m.unit}" for m in request.metrics) or "none provided"
    return _PROMPT_TEMPLATE.format(
        alert_name=request.alert.name,
        alert_severity=request.alert.severity,
        alert_description=request.alert.description or "none",
        service_name=request.deployment.service_name,
        version=request.deployment.version,
        environment=request.deployment.environment,
        metrics=metrics_str,
        log_excerpt=request.log_excerpt or "none",
    )


def analyze_bedrock(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    import boto3

    client = boto3.client("bedrock-runtime", region_name=settings.aws_region)
    prompt = _build_prompt(request)

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 600,
            "messages": [{"role": "user", "content": prompt}],
        }
    )

    response = client.invoke_model(
        modelId=settings.bedrock_model_id,
        body=body,
        contentType="application/json",
        accept="application/json",
    )
    payload = json.loads(response["body"].read())
    text = payload["content"][0]["text"]

    parsed = json.loads(text)

    return IncidentAnalysisResponse(
        summary=parsed["summary"],
        likely_cause=parsed["likely_cause"],
        supporting_evidence=parsed.get("supporting_evidence", []),
        recommended_actions=parsed.get("recommended_actions", [])[:3],
        confidence=parsed.get("confidence", "low"),
        insufficient_evidence_warning=parsed.get("insufficient_evidence_warning"),
        source="bedrock",
    )
