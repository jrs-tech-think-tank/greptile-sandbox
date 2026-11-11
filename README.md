# URL Shortener (Greptile Sandbox)

A small, deliberately clean FastAPI URL shortener used as a test bed for
experimenting with [Greptile](https://greptile.com) AI code review on GitHub
pull requests.

> ⚠️ This is a sandbox. Feature branches may contain **intentional** bugs for
> review experiments. See [`CLAUDE.md`](./CLAUDE.md) before "fixing" anything.

## Features

- Create a short link for a validated, normalized URL
- Resolve a short code via HTTP redirect
- List all links (newest first) with hit counts
- Delete a link by code

## Project layout

```
app/
  main.py        FastAPI app + lifespan DB init, /healthz
  routes.py      API endpoints (create / resolve / list / delete)
  storage.py     SQLite persistence (parameterized queries)
  ids.py         Random base62 short-code generator
  validation.py  URL validation + normalization
tests/           pytest suite (validation, ids, storage, routes)
```

Cross-file dependencies are intentional: `routes` depends on `validation`,
`ids`, and `storage`; `main` wires the router and initializes storage.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

Then visit http://127.0.0.1:8000/docs for interactive API docs.

## API

| Method | Path            | Description                              |
|--------|-----------------|------------------------------------------|
| POST   | `/links`        | Create a short link (`{"url": "..."}`)   |
| GET    | `/links`        | List all links                           |
| GET    | `/stats`        | Link stats (`{"total_links": N}`)        |
| GET    | `/{code}`       | Resolve a code (307 redirect)            |
| DELETE | `/links/{code}` | Delete a link                            |
| GET    | `/healthz`      | Health check                             |

### Example

```bash
# Create
curl -s -X POST localhost:8000/links \
  -H 'content-type: application/json' \
  -d '{"url": "https://example.com/some/long/path"}'

# Resolve (follow redirect)
curl -sL localhost:8000/<code>
```

## Tests

```bash
pytest -q
```

Each test uses an isolated temporary SQLite database.

## Configuration

- `SHORTENER_DB` — path to the SQLite file (default: `shortener.db`)
