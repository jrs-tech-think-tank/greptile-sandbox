"""API endpoints for the URL shortener.

Wires together the validation, id-generation, and storage modules.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from . import ids, storage, validation

router = APIRouter()

# How many times to retry on a short-code collision before giving up.
_MAX_CODE_ATTEMPTS = 5


class CreateLinkRequest(BaseModel):
    url: str


class LinkResponse(BaseModel):
    code: str
    url: str
    created_at: str
    hits: int

    @classmethod
    def from_link(cls, link: storage.Link) -> "LinkResponse":
        return cls(
            code=link.code,
            url=link.url,
            created_at=link.created_at,
            hits=link.hits,
        )


@router.post("/links", response_model=LinkResponse, status_code=201)
def create_link(payload: CreateLinkRequest) -> LinkResponse:
    """Create a short link for a validated, normalized URL."""
    try:
        normalized = validation.normalize_url(payload.url)
    except validation.InvalidURLError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    for _ in range(_MAX_CODE_ATTEMPTS):
        code = ids.generate_short_code()
        try:
            link = storage.create_link(code, normalized)
        except storage.DuplicateCodeError:
            continue
        return LinkResponse.from_link(link)

    raise HTTPException(
        status_code=500, detail="Could not allocate a unique short code"
    )


@router.get("/links", response_model=list[LinkResponse])
def list_links(
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(20, ge=1, le=100, description="items per page"),
) -> list[LinkResponse]:
    """List short links, newest first, one page at a time."""
    links = storage.list_links(page=page, page_size=page_size)
    return [LinkResponse.from_link(link) for link in links]


@router.delete("/links/{code}", status_code=204, response_class=Response)
def delete_link(code: str) -> Response:
    """Delete a short link by code."""
    if not storage.delete_link(code):
        raise HTTPException(status_code=404, detail="Short code not found")
    return Response(status_code=204)


@router.get("/{code}")
def resolve_link(code: str) -> RedirectResponse:
    """Resolve a short code and redirect to the original URL."""
    link = storage.get_link(code)
    if link is None:
        raise HTTPException(status_code=404, detail="Short code not found")
    storage.record_hit(code)
    return RedirectResponse(url=link.url, status_code=307)
