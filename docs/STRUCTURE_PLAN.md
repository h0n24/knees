# Project Structure Plan (Aligned to Current Layout)

This document maps the actual repository layout for the knee training tracker so contributors can quickly locate Django apps, templates, static assets, and documentation.

```
.
├── manage.py                      # Django entry point
├── apps/
│   └── backend/                   # Django project and feature apps
│       ├── config/                # Django settings, ASGI/WSGI entrypoints, URLs
│       ├── accounts/              # auth, profiles, template tags, migrations, tests
│       ├── pages/                 # public + app-facing pages with tests
│       └── training/              # training plans, sessions, migrations
├── docs/
│   ├── STRUCTURE_PLAN.md          # this file
│   └── resources/                 # briefs, prototypes, requirements, wireframes
│       ├── other/
│       ├── prototypes/
│       ├── requirements/
│       └── wireframes/
├── static/                        # static assets served by Django
│   ├── css/
│   ├── exercises/
│   ├── js/
│   └── screens/
├── templates/                     # server-rendered templates
│   ├── accounts/
│   ├── admin/
│   └── pages/
├── tests/                         # additional integration/unit tests
│   ├── backend/
│   └── frontend/
├── exercises.json                 # bundled exercise library seed
├── requirements.txt               # Python dependencies
└── README.md                      # project overview and quickstart
```

## Local Development Notes

- Create a virtual environment, install dependencies, then run migrations and the dev server: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python manage.py migrate && python manage.py runserver`.
- SQLite is the default database; switch to Postgres or MySQL by updating `apps/backend/config/settings.py`.
- Store secrets and environment variables in a local `.env` that is excluded from version control.
- Use Django admin and the bundled templates for a fully server-rendered flow.

## Navigation Mapping (per requirements)

- **Public:** Landing, About, Privacy Policy (served from `apps/backend/pages`).
- **Auth:** Signup, Login, Forgot Password (handled in `apps/backend/accounts`).
- **User:** Today, Check-in, History, Profile, Motivation banner (templates in `templates/pages/`).
- **Trainer/Admin:** Dashboard, Users list, Reports, Plan editor with auto-progression review (logic primarily in `apps/backend/training/` + `apps/backend/pages/`).

## Documentation Organization

- Requirement deltas and decisions: `docs/resources/requirements/`.
- Wireframes and prototypes: `docs/resources/wireframes/` and `docs/resources/prototypes/`.
- Additional references or supporting material: `docs/resources/other/`.
