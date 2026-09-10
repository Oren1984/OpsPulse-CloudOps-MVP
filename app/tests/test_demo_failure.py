from opspulse.demo_state import demo_failure_state


async def test_demo_status_defaults_inactive(client):
    resp = await client.get("/api/demo/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["demo_mode_enabled"] is True
    assert body["demo_failure_active"] is False


async def test_trigger_and_restore_demo_failure(client):
    trigger = await client.post("/api/demo/fail")
    assert trigger.status_code == 200
    assert trigger.json()["demo_failure_active"] is True
    assert demo_failure_state.active is True

    restore = await client.post("/api/demo/restore")
    assert restore.status_code == 200
    assert restore.json()["demo_failure_active"] is False
    assert demo_failure_state.active is False


async def test_demo_disabled_returns_403(client, monkeypatch):
    from opspulse.config import settings

    monkeypatch.setattr(settings, "demo_mode_enabled", False)
    resp = await client.post("/api/demo/fail")
    assert resp.status_code == 403
