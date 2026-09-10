from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from opspulse.db.models import Incident, Service
from opspulse.db.session import get_db

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)) -> HTMLResponse:
    services = (await db.execute(select(Service).order_by(Service.name))).scalars().all()
    incidents = (
        (await db.execute(select(Incident).order_by(Incident.created_at.desc()).limit(10)))
        .scalars()
        .all()
    )
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"services": services, "incidents": incidents},
    )
