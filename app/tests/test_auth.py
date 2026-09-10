from opspulse.config import settings


async def test_missing_api_key_is_rejected(client):
    settings.api_key = "test-api-key"
    response = await client.post(
        "/api/services",
        json={"name": "auth-check", "description": "requires key"},
    )
    assert response.status_code == 401


async def test_invalid_api_key_is_rejected(client):
    settings.api_key = "test-api-key"
    response = await client.post(
        "/api/services",
        json={"name": "bad-key", "description": "wrong key"},
        headers={"X-API-Key": "not-the-right-key"},
    )
    assert response.status_code == 403


async def test_valid_api_key_is_accepted(client):
    settings.api_key = "test-api-key"
    response = await client.post(
        "/api/services",
        json={"name": "good-key", "description": "valid key"},
        headers={"X-API-Key": "test-api-key"},
    )
    assert response.status_code == 201
