# sqlite-client-service

A minimal Flask + SQLite service for demoing Sentry performance issue detection
(specifically N+1 queries) with Cursor Automations.

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your Sentry DSN
python seed.py
python app.py
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/authors` | Lists all authors with books (**has N+1 query**) |
| GET | `/api/authors/<author_id>` | Returns one author and serialized books |
| GET | `/api/authors/<author_id>/books` | Returns one author's books |
| GET | `/health` | Health check |

## The N+1 Problem

`GET /api/authors` fetches all authors, then lazily loads each author's books
in a separate query — 1 query for authors + N queries for books = N+1.
