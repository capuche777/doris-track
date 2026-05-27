# Deployment

## Image

Built from `Python/Dockerfile` (context = repo root). It installs
`django/requirements-dev.txt` because the bundled compose service runs
`config.settings.dev`. For a production-only image, install
`django/requirements.txt` instead and run with `config.settings.prod`.

## Environment variables

Copy `.env.example` to `.env`. Keys:

| Var | Purpose | Notes |
|-----|---------|-------|
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.dev` / `config.settings.prod` |
| `DJANGO_SECRET_KEY` | Secret key | **Required** in prod (no fallback) |
| `DEBUG` | Debug mode | Forced `True` by dev settings |
| `ALLOWED_HOSTS` | Comma-separated hosts | Required in prod |

## Run

```bash
docker compose up --build      # or: make build && make run
```

The service listens on `:8000` via Gunicorn (`config.wsgi:application`).

## Database

- Dev: SQLite at `django/db.sqlite3`.
- Prod: PostgreSQL — point `DATABASES` in `config/settings/prod.py` at the
  managed instance (`psycopg2-binary` is already a runtime dependency).

Apply migrations after each release: `make migrate`.

## Static files

`django/static/` plus app-level static (`apps/core/static`) are served by
WhiteNoise / staticfiles finders. Run `collectstatic` into
`django/staticfiles/` for a production build.
