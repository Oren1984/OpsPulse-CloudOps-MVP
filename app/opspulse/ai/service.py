from opspulse.ai.fallback import analyze_fallback
from opspulse.ai.mock import analyze_mock
from opspulse.ai.sanitize import sanitize_text
from opspulse.config import settings
from opspulse.logging_config import get_logger
from opspulse.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse

logger = get_logger("opspulse.ai.service")


def analyze_incident(request: IncidentAnalysisRequest) -> IncidentAnalysisResponse:
    """Dispatch to the configured AI backend with a safe, deterministic fallback.

    Never raises: any backend failure degrades to the fallback analyzer so
    the endpoint always returns a structured, clearly-labeled response.
    """
    sanitized = request.model_copy(
        update={"log_excerpt": sanitize_text(request.log_excerpt, settings.ai_max_log_chars)}
    )

    backend = settings.ai_backend.lower()

    if backend == "mock":
        return analyze_mock(sanitized)

    if backend == "bedrock":
        try:
            from opspulse.ai.bedrock import analyze_bedrock

            return analyze_bedrock(sanitized)
        except Exception as exc:  # noqa: BLE001 - any Bedrock failure must degrade safely
            logger.warning("bedrock_analysis_failed", error=str(exc))
            return analyze_fallback(sanitized)

    return analyze_fallback(sanitized)
