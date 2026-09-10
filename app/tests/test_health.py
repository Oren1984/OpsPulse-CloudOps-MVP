async def test_liveness_ok(client):
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"


async def test_readiness_ok(client):
    resp = await client.get("/readyz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["database"] is True


async def test_readiness_degraded_during_demo_failure(client):
    trigger = await client.post("/api/demo/fail", headers={"X-API-Key": "test-api-key"})
    assert trigger.status_code == 200

    resp = await client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["status"] == "degraded"

    restore = await client.post("/api/demo/restore", headers={"X-API-Key": "test-api-key"})
    assert restore.status_code == 200

    resp2 = await client.get("/readyz")
    assert resp2.status_code == 200
