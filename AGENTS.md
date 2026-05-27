# DorisTrack — Agent Instructions

Shared conventions for any AI agent or contributor working on this repo.

## Stack
- Django 5.2 (LTS), server-rendered templates (no REST API — `rest_framework`
  is installed but unused for now)
- SQLite (dev) / PostgreSQL (prod)
- Gunicorn + WhiteNoise
- pytest + pytest-django, run inside Docker

## Layout
- `django/` — backend root (this is `BASE_DIR`)
  - `apps/<app>/` — one bounded context per app: `models.py`, `views.py`,
    `urls.py`, `services.py` (business logic), `selectors.py` (read queries),
    `admin.py`, `migrations/`, `tests/`
  - `config/` — `settings/{base,dev,prod}.py`, `urls.py`, `wsgi.py`, `asgi.py`
  - `core/` — cross-cutting utilities (`exceptions.py`, `mixins.py`,
    `pagination.py`, `permissions.py`); not a domain app
  - `templates/` — global server-rendered templates, one subfolder per feature
  - `static/` — global static assets (most live in `apps/core/static`)
  - `requirements.txt` (runtime) / `requirements-dev.txt` (test + debug tooling)
- `Python/Dockerfile` — image build
- `docs/` — `architecture.md`, `deployment.md`

## Conventions
- Class-Based Views preferred (see Rule 4); business logic in `services.py` (SoC)
- Read queries that span models go in `selectors.py` (DRY)
- All comments, docstrings and user-facing strings in English
- Error codes: `UPPERCASE_SNAKE_CASE`
- PEP8; 4-space indent

## Commands (Docker)
- `make test` — run the full test suite
- `make migrate` — apply migrations
- `make makemigrations` — generate migrations
- `make run` — start the dev stack (`docker compose up`)
- `make shell` — Django shell in the running container

## Notes
- Tests run only inside the Docker container, not on the host.
- After editing Python, the gunicorn container needs a restart to pick changes
  up (templates/static are served live via the bind mount).
