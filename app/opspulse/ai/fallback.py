"""Deterministic, rule-based fallback analysis.

Used whenever Bedrock is disabled, unreachable, or errors. It produces a
best-effort structured response from the bounded context alone, without
any external model call, and always self-identifies as "fallback".
"""

from opspulse.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse


def analyze_fallback(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    evidence: list[str] = [f"Alert: {request.alert.name} ({request.alert.severity})"]
    if request.alert.description:
        evidence.append(request.alert.description)

    high_metrics = [
        m for m in request.metrics if m.name.lower() in {"error_rate", "p95_latency_ms", "cpu_percent"}
    ]
    for metric in high_metrics:
        evidence.append(f"{metric.name} = {metric.value}{metric.unit}")

    has_log = bool(request.log_excerpt.strip())
    if has_log:
        evidence.append("Log excerpt provided (see incident context)")

    likely_cause = "Insufficient data to determine root cause automatically."
    confidence = "low"
    warning = (
        "Evidence is insufficient for a confident automated diagnosis. "
        "Manual investigation is recommended."
    )

    name_lower = request.alert.name.lower()
    if "latency" in name_lower or any("latency" in m.name.lower() for m in request.metrics):
        likely_cause = (
            "Elevated latency, consistent with resource saturation, a slow "
            "downstream dependency, or a recent deployment regression."
        )
        confidence = "medium" if has_log else "low"
        warning = None if has_log else warning
    elif "error" in name_lower or any("error" in m.name.lower() for m in request.metrics):
        likely_cause = (
            "Elevated error rate, consistent with a bad deployment, an "
            "upstream/database dependency failure, or a recent code regression."
        )
        confidence = "medium" if has_log else "low"
        warning = None if has_log else warning
    elif "database" in name_lower or "postgres" in name_lower:
        likely_cause = "Database connectivity or availability issue."
        confidence = "medium"
        warning = None

    actions = [
        f"Check recent deployments for {request.deployment.service_name} "
        f"(version {request.deployment.version}, {request.deployment.environment}).",
        "Inspect the linked Grafana dashboard for the affected time window.",
        "Review application logs around the alert timestamp for stack traces or repeated errors.",
    ]

    return IncidentAnalysisResponse(
        summary=(
            f"Automated (fallback) analysis of alert '{request.alert.name}' "
            f"for service '{request.deployment.service_name}'."
        ),
        likely_cause=likely_cause,
        supporting_evidence=evidence,
        recommended_actions=actions[:3],
        confidence=confidence,
        insufficient_evidence_warning=warning,
        source="fallback",
    )
