# Project Structure Plan (Local-First)

This plan models a folder structure that satisfies the functional scope in `README.md` and the creative direction in `CREATIVE-BRIEF.md`, optimized for straightforward local development with a single Django app serving HTML, CSS, and vanilla JavaScript.

```
.
├── apps/
│   ├── backend/                     # Django project (API + admin)
│   │   ├── config/                  # Django settings, ASGI entry
│   │   ├── accounts/                # auth, roles, profile models
│   │   ├── training/                # plans, plan items, logs
│   │   ├── checkins/                # daily recovery inputs
│   │   ├── reports/                 # aggregation + dashboards
│   │   └── pages/                   # about/privacy pages
├── docs/
│   ├── STRUCTURE_PLAN.md            # this file
│   └── resources/
│       ├── requirements/            # requirements snapshots, briefs
│       └── wireframes/              # design PDFs
├── tests/
│   ├── backend/                     # Django unit/integration tests
│   └── frontend/                    # Browser-driven UI tests for templates
├── static/                          # collected static files for Django
├── templates/                       # Django templates for server-rendered fallbacks
├── exercises.json                   # seed data for starter plans
└── README.md                        # project overview
```

## Local Development Notes

- Use the provided `manage.py` commands for migrations and running the Django server (`python manage.py migrate` and `python manage.py runserver`).
- The default database is SQLite for quick local spins; swap to Postgres/MySQL later by updating Django settings.
- Run the Django server locally with `python manage.py runserver` to serve both pages and APIs.
- Keep environment variables in a local `.env` file (ignored from version control) for secrets and DB URLs.

## Navigation Mapping (per requirements)

- **Public:** Landing page, About, Privacy Policy.
- **Auth:** Signup, Login, Forgot Password.
- **User:** Today, Check-in, History, Profile, Motivation banner.
- **Trainer/Admin:** Dashboard, Users list, Reports (daily/weekly/monthly), Plan editor with auto-progression review.

## Future Documentation Organization

- Use `docs/resources/requirements` to capture requirement deltas and decision logs.
- Keep wireframes in `docs/resources/wireframes` to align designers and developers.
- Add API contracts (`docs/api/`) and data models (`docs/data-models/`) once finalized.
