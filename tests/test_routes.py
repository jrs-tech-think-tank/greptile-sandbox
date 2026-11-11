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


def _seed_links(client, n):
    """Create ``n`` links and return their codes in creation order."""
    codes = []
    for i in range(n):
        resp = client.post("/links", json={"url": f"https://example.com/{i}"})
        assert resp.status_code == 201
        codes.append(resp.json()["code"])
    return codes


def _page_codes(client, page, page_size):
    resp = client.get("/links", params={"page": page, "page_size": page_size})
    assert resp.status_code == 200
    return [item["code"] for item in resp.json()]


def test_list_default_page_returns_saved_links(client):
    created = _seed_links(client, 3)
    resp = client.get("/links")
    assert resp.status_code == 200
    body = resp.json()
    # The default first page must contain exactly the saved links (the bug
    # returned an empty list here).
    assert sorted(item["code"] for item in body) == sorted(created)


def test_list_pagination_exact_pages(client):
    created = _seed_links(client, 5)

    # Canonical newest-first order, taken from a single full page.
    full = client.get("/links", params={"page": 1, "page_size": 100}).json()
    full_codes = [item["code"] for item in full]
    assert sorted(full_codes) == sorted(created)
    # Confirm the full ordering really is newest-first by created_at.
    created_ats = [item["created_at"] for item in full]
    assert created_ats == sorted(created_ats, reverse=True)

    # Consecutive pages of size 2 are exact, non-overlapping slices.
    assert _page_codes(client, 1, 2) == full_codes[0:2]
    assert _page_codes(client, 2, 2) == full_codes[2:4]
    assert _page_codes(client, 3, 2) == full_codes[4:6]  # last, one item

    # The page after the final result is empty.
    assert _page_codes(client, 4, 2) == []


def test_list_page_size_bounds(client):
    # page_size is capped at 100 and must be >= 1; page is 1-based.
    assert client.get("/links", params={"page_size": 100}).status_code == 200
    assert client.get("/links", params={"page_size": 101}).status_code == 422
    assert client.get("/links", params={"page_size": 0}).status_code == 422
    assert client.get("/links", params={"page": 0}).status_code == 422


def test_list_huge_page_returns_empty_not_error(client):
    _seed_links(client, 2)
    # A page far beyond the data must return an empty page, not a 500.
    resp = client.get("/links", params={"page": 10**18, "page_size": 100})
    assert resp.status_code == 200
    assert resp.json() == []
