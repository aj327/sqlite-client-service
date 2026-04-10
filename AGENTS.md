# Agent Guide — sqlite-client-service

A minimal Flask + SQLAlchemy + SQLite service used for demoing Sentry
performance and error detection with Cursor Automations.

## Environment setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Seed the database (only needed once)

```bash
python seed.py
```

## Run the server

```bash
python app.py          # starts on http://127.0.0.1:5001
```

## Run tests

```bash
python -m pytest test_api.py -v
# or
python -m unittest test_api.py -v
```

## Project structure

| File | Purpose |
|------|---------|
| `app.py` | Flask application and route definitions |
| `models.py` | SQLAlchemy models — `Author` and `Book` |
| `seed.py` | Populates the database with sample data |
| `test_api.py` | API endpoint regression tests |
| `requirements.txt` | Python dependencies |

## Key patterns

- **Models** are in `models.py`. If adding serialization, add `to_dict()` methods on the model classes.
- **Routes** are defined inside `create_app()` in `app.py`.
- `create_app()` accepts `database_uri` and `enable_sentry` params for testing.
- Always handle missing resources with a 404 response.

## Sentry

- DSN is loaded from the `SENTRY_DSN` environment variable (set in `.env`).
- Performance tracing and profiling are enabled at 100% sample rate.
- The SQLAlchemy and Flask integrations are auto-detected by the SDK.
