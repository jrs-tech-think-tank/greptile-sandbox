"""End-to-end API tests using FastAPI's TestClient."""


def test_create_resolve_list_delete_flow(client):
    # Create
    resp = client.post("/links", json={"url": "http://Example.com/Path"})
    assert resp.status_code == 201
    body = resp.json()
    code = body["code"]
    assert body["url"] == "http://example.com/Path"  # normalized
    assert body["hits"] == 0

    # List
    resp = client.get("/links")
    assert resp.status_code == 200
    assert any(item["code"] == code for item in resp.json())

    # Resolve (no auto-follow so we can inspect the redirect)
    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "http://example.com/Path"

    # Hit counter incremented
    resp = client.get("/links")
    item = next(i for i in resp.json() if i["code"] == code)
    assert item["hits"] == 1

    # Delete
    resp = client.delete(f"/links/{code}")
    assert resp.status_code == 204

    # Now resolves to 404
    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 404


def test_create_rejects_invalid_url(client):
    resp = client.post("/links", json={"url": "not-a-url"})
    assert resp.status_code == 422


def test_delete_missing_returns_404(client):
    resp = client.delete("/links/nope123")
    assert resp.status_code == 404


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
