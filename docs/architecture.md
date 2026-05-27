# Architecture

DorisTrack is a single-student English learning tracker. It is a server-rendered
Django application — templates and views only, no client-side SPA and no public
REST API.

## High-level

```
Browser ──HTTP──▶ Gunicorn ──▶ Django (config.wsgi)
                                  │
                                  ├─ apps/* (views → services/selectors → models)
                                  ├─ templates/ (server-rendered HTML)
                                  └─ SQLite (dev) / PostgreSQL (prod)
```

## Apps (bounded contexts)

| App | Responsibility |
|-----|----------------|
| `profiles` | The student profile and tutor (domain `Student`) |
| `vocabulary` | Word bank + spaced repetition (SM-2) |
| `scores` | Assessments and per-skill scores |
| `quiz` | Weekly quiz generation and results |
| `grammar` | Grammar correction log + analytics |
| `practice` | Practice sessions, streaks, heatmap |
| `dashboard` | Aggregated home view (reads `core.selectors`) |
| `students` | Legacy `Student` model linked to `auth.User` |
| `core` | Cross-app dashboard selectors, templatetags, design-system static |

## Layering (SoC)

- **views** — HTTP handling, delegate to services/selectors, render templates
- **services** — business logic and writes
- **selectors** — read-only queries, including cross-app aggregation in
  `apps/core/selectors.py`
- **models** — data structure and validation

## Paths

`BASE_DIR` is the `django/` directory. Templates live in `django/templates/`
(one subfolder per feature), global static in `django/static/`, the dev database
at `django/db.sqlite3`.
