# Project Structure Plan (Vercel-Friendly)

This plan models a folder structure that satisfies the functional scope in `README.md` and the creative direction in `CREATIVE-BRIEF.md`, while fitting within free Vercel hosting (serverless-friendly, minimal cold-start risk).

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
│   └── frontend/                    # Next.js (App Router) UI
│       ├── app/                     # routes for landing, auth, dashboards
│       │   ├── (marketing)/         # landing page sections
│       │   ├── (auth)/              # signup/login/forgot password
│       │   ├── (user)/              # Today, Check-in, History
│       │   ├── (trainer)/           # Dashboard, Users, Reports, Plans
│       │   └── api/                 # server actions or fetch wrappers
│       ├── components/              # shared UI per creative brief
│       ├── lib/                     # API client, auth helpers
│       ├── styles/                  # tokens + global styles
│       └── public/                  # static assets
├── api/
│   ├── django.py                    # Vercel Python serverless entry (ASGI via config.asgi:application)
│   └── healthcheck.py               # lightweight uptime probe
├── docs/
│   ├── STRUCTURE_PLAN.md            # this file
│   └── resources/
│       ├── requirements/            # requirements snapshots, briefs
│       └── wireframes/              # design PDFs
├── infra/
│   ├── vercel.json                  # routes build output to Next.js + Django ASGI
│   └── scripts/                     # deploy/build helpers (collectstatic, migrations)
├── tests/
│   ├── backend/                     # Django unit/integration tests
│   └── frontend/                    # Playwright/React tests
├── static/                          # collected static files (Vercel storage bucket/CDN)
├── templates/                       # Django templates for server-rendered fallbacks
├── exercises.json                   # seed data for starter plans
└── README.md                        # project overview
```

## Vercel-Specific Notes

- Keep **serverless functions small and fast**: the Django ASGI entry in `api/django.py` should import only what is needed and rely on environment variables for settings. Avoid long-lived background work.
- Use **Vercel Postgres / Neon** (or another hosted DB) via environment variables; do not rely on local SQLite in production.
- Prefer **Next.js static generation or ISR** for marketing/auth shells. Authenticated pages can use server actions or API fetches to the Django endpoints deployed as serverless functions.
- Store large assets (e.g., media) in object storage (S3-compatible) referenced by URLs rather than bundling into the repo.
- Include a **healthcheck** endpoint so Vercel uptime monitors the Python function without exercising full business logic.

## Navigation Mapping (per requirements)

- **Public:** Landing page, About, Privacy Policy.
- **Auth:** Signup, Login, Forgot Password.
- **User:** Today, Check-in, History, Profile, Motivation banner.
- **Trainer/Admin:** Dashboard, Users list, Reports (daily/weekly/monthly), Plan editor with auto-progression review.

## Future Documentation Organization

- Use `docs/resources/requirements` to capture requirement deltas and decision logs.
- Keep wireframes in `docs/resources/wireframes` to align designers and developers.
- Add API contracts (`docs/api/`) and data models (`docs/data-models/`) once finalized.
