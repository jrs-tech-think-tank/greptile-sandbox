"""End-to-end API tests using FastAPI's TestClient."""

from app import storage


def test_create_resolve_list_delete_flow(client):
    # Create
    resp = client.post("/links", json={"url": "http://Example.com/Path"})
    assert resp.status_code == 201
    body = resp.json()
    code = body["code"]
    assert body["url"] == "http://example.com/Path"  # normalized
    assert body["hits"] == 0
    assert storage.get_link(code) is not None

    # List returns a JSON array
    resp = client.get("/links")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

    # Resolve (no auto-follow so we can inspect the redirect)
    resp = client.get(f"/{code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "http://example.com/Path"

    # Hit counter incremented
    assert storage.get_link(code).hits == 1

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


def _seed_links(client, n):
    for i in range(n):
        client.post("/links", json={"url": f"https://example.com/{i}"})


def test_list_pagination_returns_list(client):
    _seed_links(client, 3)
    resp = client.get("/links")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) <= 20  # default page_size


def test_list_page_size_bounds(client):
    # page_size is capped at 100 and must be >= 1; page is 1-based.
    assert client.get("/links", params={"page_size": 100}).status_code == 200
    assert client.get("/links", params={"page_size": 101}).status_code == 422
    assert client.get("/links", params={"page_size": 0}).status_code == 422
    assert client.get("/links", params={"page": 0}).status_code == 422


def test_list_respects_page_size(client):
    _seed_links(client, 5)
    resp = client.get("/links", params={"page": 1, "page_size": 2})
    assert resp.status_code == 200
    assert len(resp.json()) <= 2
