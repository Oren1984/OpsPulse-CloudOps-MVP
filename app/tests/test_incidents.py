async def test_create_incident_requires_valid_service(client):
    resp = await client.post(
        "/api/incidents",
        json={
            "title": "test incident",
            "service_id": "00000000-0000-0000-0000-000000000000",
        },
    )
    assert resp.status_code == 404


async def test_create_and_resolve_incident(client):
    service_resp = await client.post("/api/services", json={"name": "svc-inc"})
    service_id = service_resp.json()["id"]

    incident_resp = await client.post(
        "/api/incidents",
        json={"title": "elevated errors", "service_id": service_id, "severity": "high"},
    )
    assert incident_resp.status_code == 201
    incident = incident_resp.json()
    assert incident["status"] == "open"
    assert incident["resolved_at"] is None

    resolve_resp = await client.patch(f"/api/incidents/{incident['id']}", json={"status": "resolved"})
    assert resolve_resp.status_code == 200
    resolved = resolve_resp.json()
    assert resolved["status"] == "resolved"
    assert resolved["resolved_at"] is not None


async def test_list_incidents(client):
    service_resp = await client.post("/api/services", json={"name": "svc-inc-2"})
    service_id = service_resp.json()["id"]
    await client.post("/api/incidents", json={"title": "incident A", "service_id": service_id})

    list_resp = await client.get("/api/incidents")
    assert list_resp.status_code == 200
    assert any(i["title"] == "incident A" for i in list_resp.json())
