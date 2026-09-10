"""Idempotent seed data loader.

Run with: python -m opspulse.seed
"""

import asyncio

from sqlalchemy import select

from opspulse.db.models import Incident, IncidentSeverity, IncidentStatus, Service, ServiceStatus
from opspulse.db.session import AsyncSessionLocal
from opspulse.logging_config import get_logger

logger = get_logger("opspulse.seed")

SEED_SERVICES = [
    {
        "name": "opspulse-api",
        "description": "Core FastAPI application service.",
        "endpoint_url": "http://opspulse-app:8000/healthz",
        "status": ServiceStatus.healthy,
    },
    {
        "name": "opspulse-postgres",
        "description": "Primary PostgreSQL database.",
        "endpoint_url": "postgres://opspulse-postgres:5432/opspulse",
        "status": ServiceStatus.healthy,
    },
    {
        "name": "opspulse-prometheus",
        "description": "Metrics collection.",
        "endpoint_url": "http://opspulse-prometheus:9090",
        "status": ServiceStatus.healthy,
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(Service.name))).scalars().all()
        existing_names = set(existing)

        created_services: list[Service] = []
        for entry in SEED_SERVICES:
            if entry["name"] in existing_names:
                continue
            service = Service(**entry)
            session.add(service)
            created_services.append(service)

        await session.commit()
        for s in created_services:
            await session.refresh(s)

        if created_services:
            logger.info("seed_services_created", count=len(created_services))
        else:
            logger.info("seed_services_already_present")

        api_service_result = await session.execute(select(Service).where(Service.name == "opspulse-api"))
        api_service = api_service_result.scalar_one_or_none()

        existing_incidents = (await session.execute(select(Incident.title))).scalars().all()
        if api_service and "Sample: elevated latency on opspulse-api" not in existing_incidents:
            session.add(
                Incident(
                    service_id=api_service.id,
                    title="Sample: elevated latency on opspulse-api",
                    description="Seed incident demonstrating the incident feed. Resolved sample data.",
                    severity=IncidentSeverity.medium,
                    status=IncidentStatus.resolved,
                )
            )
            await session.commit()
            logger.info("seed_incident_created")


if __name__ == "__main__":
    asyncio.run(seed())
