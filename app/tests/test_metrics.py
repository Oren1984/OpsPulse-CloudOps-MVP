async def test_metrics_endpoint_exposes_prometheus_format(client):
    await client.get("/healthz")

    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    body = resp.text
    assert "opspulse_http_requests_total" in body
    assert "opspulse_build_info" in body
