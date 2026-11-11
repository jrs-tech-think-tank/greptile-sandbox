"""Application entry point.

Run locally with:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import storage
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure the database schema exists before serving requests.
    storage.init_db()
    yield


app = FastAPI(title="URL Shortener", version="0.1.0", lifespan=lifespan)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


# Include the router last so the catch-all ``GET /{code}`` resolver does not
# shadow fixed routes like ``/healthz``.
app.include_router(router)
