import os

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("AI_BACKEND", "mock")
os.environ.setdefault("DEMO_MODE_ENABLED", "true")
os.environ.setdefault("API_KEY", "test-api-key")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from opspulse.db.base import Base
from opspulse.db.session import get_db
from opspulse.demo_state import demo_failure_state
from opspulse.main import app


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(bind=db_engine, expire_on_commit=False, class_=AsyncSession)

    async def _override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = _override_get_db
    demo_failure_state.restore()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    demo_failure_state.restore()


@pytest.fixture
def anyio_backend():
    return "asyncio"
