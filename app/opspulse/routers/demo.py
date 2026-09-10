from fastapi import APIRouter, Depends, HTTPException

from opspulse.auth import require_api_key
from opspulse.config import settings
from opspulse.demo_state import demo_failure_state

router = APIRouter(prefix="/api/demo", tags=["demo"])


def _require_demo_mode() -> None:
    if not settings.demo_mode_enabled:
        raise HTTPException(
            status_code=403,
            detail="Demo-failure mechanism is disabled (DEMO_MODE_ENABLED=false).",
        )


@router.post("/fail")
async def trigger_demo_failure(_: str = Depends(require_api_key)) -> dict:
    """Trigger a controlled, reversible demo failure. Dev/demo only."""
    _require_demo_mode()
    demo_failure_state.trigger()
    return {"demo_failure_active": True}


@router.post("/restore")
async def restore_demo_failure(_: str = Depends(require_api_key)) -> dict:
    """Restore the system from the controlled demo failure."""
    _require_demo_mode()
    demo_failure_state.restore()
    return {"demo_failure_active": False}


@router.get("/status")
async def demo_status() -> dict:
    return {"demo_mode_enabled": settings.demo_mode_enabled, "demo_failure_active": demo_failure_state.active}
