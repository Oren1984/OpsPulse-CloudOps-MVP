from fastapi import APIRouter, Response

from opspulse.config import settings
from opspulse.db.session import db_is_reachable
from opspulse.demo_state import demo_failure_state
from opspulse.metrics import DATABASE_UP
from opspulse.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/healthz", response_model=HealthOut)
async def liveness() -> HealthOut:
    """Liveness: process is up. Does not depend on the database."""
    return HealthOut(status="ok", database=True, demo_mode=settings.demo_mode_enabled)


@router.get("/readyz", response_model=HealthOut)
async def readiness(response: Response) -> HealthOut:
    """Readiness: process is up AND its dependencies (database) are reachable."""
    db_ok = await db_is_reachable()
    DATABASE_UP.set(1 if db_ok else 0)

    demo_degraded = demo_failure_state.active
    healthy = db_ok and not demo_degraded

    if not healthy:
        response.status_code = 503

    status = "ok" if healthy else "degraded"
    return HealthOut(status=status, database=db_ok, demo_mode=settings.demo_mode_enabled)
