import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from opspulse.auth import require_api_key
from opspulse.db.models import Incident, IncidentStatus, Service
from opspulse.db.session import get_db
from opspulse.metrics import INCIDENTS_TOTAL
from opspulse.schemas import IncidentCreate, IncidentOut, IncidentUpdate

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


async def _refresh_open_incident_gauge(db: AsyncSession) -> None:
    result = await db.execute(
        select(func.count()).select_from(Incident).where(Incident.status != IncidentStatus.resolved)
    )
    INCIDENTS_TOTAL.set(result.scalar_one())


@router.get("", response_model=list[IncidentOut])
async def list_incidents(db: AsyncSession = Depends(get_db)) -> list[Incident]:
    result = await db.execute(select(Incident).order_by(Incident.created_at.desc()))
    return list(result.scalars().all())


@router.post("", response_model=IncidentOut, status_code=201)
async def create_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
) -> Incident:
    service = await db.get(Service, payload.service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    incident = Incident(**payload.model_dump())
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    await _refresh_open_incident_gauge(db)
    return incident


@router.get("/{incident_id}", response_model=IncidentOut)
async def get_incident(incident_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Incident:
    incident = await db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}", response_model=IncidentOut)
async def update_incident(
    incident_id: uuid.UUID,
    payload: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
) -> Incident:
    incident = await db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    updates = payload.model_dump(exclude_unset=True)
    if updates.get("status") == IncidentStatus.resolved and incident.resolved_at is None:
        incident.resolved_at = datetime.now(UTC)

    for field, value in updates.items():
        setattr(incident, field, value)

    await db.commit()
    await db.refresh(incident)
    await _refresh_open_incident_gauge(db)
    return incident
