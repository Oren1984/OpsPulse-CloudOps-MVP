async def test_create_and_list_service(client):
    payload = {"name": "test-svc", "description": "demo", "endpoint_url": "http://x/health"}
    create_resp = await client.post("/api/services", json=payload, headers={"X-API-Key": "test-api-key"})
    assert create_resp.status_code == 201
    created = create_resp.json()
    assert created["name"] == "test-svc"
    assert created["status"] == "unknown"

    list_resp = await client.get("/api/services")
    assert list_resp.status_code == 200
    names = [s["name"] for s in list_resp.json()]
    assert "test-svc" in names


async def test_get_missing_service_404(client):
    resp = await client.get("/api/services/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


async def test_update_service_status(client):
    create_resp = await client.post("/api/services", json={"name": "svc-2"}, headers={"X-API-Key": "test-api-key"})
    service_id = create_resp.json()["id"]

    patch_resp = await client.patch(
        f"/api/services/{service_id}",
        json={"status": "degraded"},
        headers={"X-API-Key": "test-api-key"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "degraded"


async def test_delete_service(client):
    create_resp = await client.post("/api/services", json={"name": "svc-3"}, headers={"X-API-Key": "test-api-key"})
    service_id = create_resp.json()["id"]

    delete_resp = await client.delete(f"/api/services/{service_id}", headers={"X-API-Key": "test-api-key"})
    assert delete_resp.status_code == 204

    get_resp = await client.get(f"/api/services/{service_id}")
    assert get_resp.status_code == 404
