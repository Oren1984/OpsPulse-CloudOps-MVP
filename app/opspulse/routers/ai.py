from fastapi import APIRouter, Depends

from opspulse.ai.service import analyze_incident
from opspulse.auth import require_api_key
from opspulse.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/analyze", response_model=IncidentAnalysisResponse)
async def analyze(
    request: IncidentAnalysisRequest,
    _: str = Depends(require_api_key),
) -> IncidentAnalysisResponse:
    """Read-only AI Incident Assistant.

    Accepts a bounded, sanitized incident context and returns a structured
    analysis. Never executes commands and never changes infrastructure.
    """
    return analyze_incident(request)
