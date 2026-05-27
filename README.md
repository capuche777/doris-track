# DorisTrack

A Django-based learning progress tracker for a single student.

## Structure

```
doris-track/
├── django/
│   ├── manage.py
│   ├── apps/                # One bounded context per app
│   │   ├── profiles/        # Student + tutor (domain models)
│   │   ├── vocabulary/      # Word bank + spaced repetition
│   │   ├── scores/          # Assessments and scores
│   │   ├── quiz/            # Weekly quizzes
│   │   ├── grammar/         # Grammar corrections
│   │   ├── practice/        # Practice sessions / streaks
│   │   ├── dashboard/       # Aggregated dashboard view
│   │   ├── students/        # Legacy Student <-> auth.User
│   │   └── core/            # Cross-app selectors, templatetags, static
│   ├── config/
│   │   ├── settings/        # base.py, dev.py, prod.py
│   │   ├── urls.py, wsgi.py, asgi.py
│   ├── core/                # Cross-cutting utils (exceptions, mixins, ...)
│   ├── templates/           # Global templates (one subfolder per feature)
│   ├── static/              # Global static assets
│   ├── requirements.txt     # Runtime deps
│   └── requirements-dev.txt # Test + debug tooling
├── Python/Dockerfile
├── docs/                    # architecture.md, deployment.md
├── pytest.ini
├── AGENTS.md
└── docker-compose.yml
```

## Setup (Development)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (use requirements-dev.txt for tests + debug tooling)
pip install -r django/requirements-dev.txt

# Run migrations
python django/manage.py migrate

# Create superuser
python django/manage.py createsuperuser

# Run server
python django/manage.py runserver
```

## Setup (Docker)

```bash
docker compose up --build
```

## Tech Stack

- Django 5.x
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod)
- Gunicorn
- D2Clic Brand: Navy `#0D1B2A`, Gold `#D4A843`, Bone `#F9F7F4`
- Fonts: Nunito (headings), DM Sans (body)

## Features

- Vocabulary bank with spaced repetition (SM-2 algorithm)
- Daily score tracking with Chart.js visualization
- Weekly quiz generation
- Grammar corrections log
- Student dashboard