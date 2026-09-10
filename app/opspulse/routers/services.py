import asyncio
import random
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from opspulse.auth import require_api_key
from opspulse.db.models import Service
from opspulse.db.session import get_db
from opspulse.demo_state import demo_failure_state
from opspulse.schemas import ServiceCreate, ServiceOut, ServiceUpdate

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceOut])
async def list_services(db: AsyncSession = Depends(get_db)) -> list[Service]:
    if demo_failure_state.active:
        # Controlled, reversible fault injection for the demo scenario only.
        await asyncio.sleep(1.2)
        if random.random() < 0.6:
            raise HTTPException(status_code=503, detail="Simulated demo-failure: upstream unavailable")

    result = await db.execute(select(Service).order_by(Service.name))
    return list(result.scalars().all())


@router.post("", response_model=ServiceOut, status_code=201)
async def create_service(
    payload: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
) -> Service:
    service = Service(**payload.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.get("/{service_id}", response_model=ServiceOut)
async def get_service(service_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Service:
    service = await db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.patch("/{service_id}", response_model=ServiceOut)
async def update_service(
    service_id: uuid.UUID,
    payload: ServiceUpdate,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
) -> Service:
    service = await db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: str = Depends(require_api_key),
) -> None:
    service = await db.get(Service, service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    await db.delete(service)
    await db.commit()
