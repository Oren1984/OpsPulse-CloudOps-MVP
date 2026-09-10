"""Real PostgreSQL integration test.

Spins up a disposable postgres:16-alpine container via the Docker CLI for
the duration of this module, applies Alembic migrations against it, and
performs a real round-trip write/read. Skipped automatically when Docker
is unavailable (e.g. some CI runners) rather than failing the suite.
"""

import shutil
import subprocess
import time
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

CONTAINER_NAME = "opspulse-pg-integration-test"
HOST_PORT = 55433

pytestmark = pytest.mark.skipif(shutil.which("docker") is None, reason="docker CLI not available")


def _docker(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", *args], capture_output=True, text=True)


@pytest.fixture(scope="module")
def postgres_container():
    _docker("rm", "-f", CONTAINER_NAME)
    run = _docker(
        "run",
        "-d",
        "--name",
        CONTAINER_NAME,
        "-e",
        "POSTGRES_USER=opspulse",
        "-e",
        "POSTGRES_PASSWORD=opspulse",
        "-e",
        "POSTGRES_DB=opspulse",
        "-p",
        f"{HOST_PORT}:5432",
        "postgres:16-alpine",
    )
    if run.returncode != 0:
        pytest.skip(f"could not start postgres container: {run.stderr}")

    try:
        for _ in range(30):
            ready = _docker("exec", CONTAINER_NAME, "pg_isready", "-U", "opspulse")
            if ready.returncode == 0:
                break
            time.sleep(1)
        else:
            pytest.skip("postgres container did not become ready in time")

        subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=__file__.rsplit("tests", 1)[0],
            env={
                **__import__("os").environ,
                "DATABASE_URL": f"postgresql+psycopg2://opspulse:opspulse@localhost:{HOST_PORT}/opspulse",
            },
            check=True,
        )

        yield f"postgresql+asyncpg://opspulse:opspulse@localhost:{HOST_PORT}/opspulse"
    finally:
        _docker("rm", "-f", CONTAINER_NAME)


@pytest_asyncio.fixture
async def pg_engine(postgres_container):
    engine = create_async_engine(postgres_container)
    yield engine
    await engine.dispose()


async def test_postgres_round_trip(pg_engine):
    async with pg_engine.begin() as conn:
        await conn.execute(text("SELECT 1"))

    service_id = str(uuid.uuid4())
    async with pg_engine.begin() as conn:
        await conn.execute(
            text(
                "INSERT INTO services (id, name, description, endpoint_url, status) "
                "VALUES (:id, :name, '', '', 'healthy')"
            ),
            {"id": service_id, "name": f"integration-{service_id[:8]}"},
        )
        result = await conn.execute(
            text("SELECT name, status FROM services WHERE id = :id"), {"id": service_id}
        )
        row = result.one()
        assert row.status == "healthy"
