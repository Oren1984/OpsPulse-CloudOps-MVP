"""Canned response used in tests and demos without live AI access.

Never claims a real model invocation occurred; always self-identifies
via `source="mock"` so callers cannot mistake it for a real Bedrock result.
"""

from opspulse.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse


def analyze_mock(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    return IncidentAnalysisResponse(
        summary=f"Mocked analysis of alert '{request.alert.name}'.",
        likely_cause="Simulated cause: mock backend does not perform real inference.",
        supporting_evidence=[f"Alert severity: {request.alert.severity}", "This is mocked test data."],
        recommended_actions=[
            "This is a mocked response for testing; take no real action.",
            "Verify AI_BACKEND configuration if you expected a live analysis.",
        ],
        confidence="low",
        insufficient_evidence_warning="Mock backend in use — not a real analysis.",
        source="mock",
    )
