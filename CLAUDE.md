# CLAUDE.md

## Project

A small FastAPI URL shortener backed by SQLite. It exposes endpoints to create
a short link, resolve a code (HTTP redirect), list links, and delete a link.

## Layout

- `app/main.py` — FastAPI app, lifespan DB initialization, `/healthz`
- `app/routes.py` — API endpoints (create / resolve / list / delete)
- `app/storage.py` — SQLite persistence (parameterized queries)
- `app/ids.py` — short-code generation
- `app/validation.py` — URL validation and normalization
- `tests/` — pytest suite

## Running locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Interactive API docs are then at http://127.0.0.1:8000/docs.

## Tests

```bash
pytest -q
```

Each test runs against an isolated temporary SQLite database.

## Code style

- Python 3.12; standard library plus FastAPI / Pydantic.
- `from __future__ import annotations` at the top of modules; type hints on
  public functions.
- Keep modules small and single-purpose: `routes` depends on `validation`,
  `ids`, and `storage`.
- Use parameterized SQL queries only.

See [`README.md`](./README.md) for the full API reference and examples.
