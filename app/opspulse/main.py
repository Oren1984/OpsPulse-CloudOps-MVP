import re
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from opspulse import __version__
from opspulse.config import settings
from opspulse.logging_config import configure_logging, get_logger
from opspulse.metrics import (
    BUILD_INFO,
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)
from opspulse.routers import ai, dashboard, demo, health, incidents, metrics_router, services

configure_logging()
logger = get_logger("opspulse.main")


@asynccontextmanager
async def lifespan(_: FastAPI):
    BUILD_INFO.labels(version=__version__, environment=settings.app_env).set(1)
    logger.info("opspulse_startup", version=__version__, environment=settings.app_env)
    yield


app = FastAPI(
    title="OpsPulse",
    description="POC/MVP cloud-ops demo application. Not production-ready.",
    version=__version__,
    lifespan=lifespan,
)

_UUID_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)


def _normalize_path(path: str) -> str:
    """Collapse path params so metric label cardinality stays bounded."""
    return _UUID_RE.sub("{id}", path)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    path = _normalize_path(request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        HTTP_ERRORS_TOTAL.labels(method=request.method, path=path).inc()
        HTTP_REQUESTS_TOTAL.labels(method=request.method, path=path, status_code="500").inc()
        raise
    duration = time.perf_counter() - start
    HTTP_REQUEST_DURATION_SECONDS.labels(method=request.method, path=path).observe(duration)
    HTTP_REQUESTS_TOTAL.labels(
        method=request.method, path=path, status_code=str(response.status_code)
    ).inc()
    if response.status_code >= 500:
        HTTP_ERRORS_TOTAL.labels(method=request.method, path=path).inc()
    return response


app.include_router(health.router)
app.include_router(metrics_router.router)
app.include_router(services.router)
app.include_router(incidents.router)
app.include_router(demo.router)
app.include_router(ai.router)
app.include_router(dashboard.router)
