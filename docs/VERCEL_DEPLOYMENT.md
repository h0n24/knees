# Deploying the Knee Training Tracker Skeleton to Vercel

This checklist walks through deploying the dual Django + Next.js skeleton to Vercel. It assumes you have the Vercel CLI installed and a Vercel account.

## 1) Prepare environment
- Install dependencies locally:
  - Python: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
  - Node: `cd apps/frontend && npm install`
- Create environment variables in Vercel (Project Settings → Environment Variables):
  - `DJANGO_SECRET_KEY` — generate a secure value.
  - `DJANGO_DEBUG` — set to `False` in production.
  - `DJANGO_ALLOWED_HOSTS` — e.g., `your-project.vercel.app`.
  - `DATABASE_URL` — e.g., Vercel Postgres/Neon URL.

## 2) Configure Vercel project
- From the repo root, run `vercel init` (or connect via the Vercel dashboard) and select a monorepo project.
- Set **Root Directory** to the repo root (so both Next.js and `api/` are available).
- Ensure the build command for the frontend is `npm run build` with the output directory auto-detected by Vercel (`.next`).

## 3) Python (Django) function
- Vercel will build the Python function from `api/django.py` using `requirements.txt` at the repo root.
- For local testing of the ASGI entrypoint, run `DJANGO_SETTINGS_MODULE=apps.backend.config.settings uvicorn api.django:application --reload`.
- Migrations/collectstatic can be run via `infra/scripts` hooks (to be filled in future milestones).

## 4) Frontend (Next.js)
- The Next.js app lives in `apps/frontend/` and uses the App Router with a standalone output for Vercel.
- Local dev: `cd apps/frontend && npm run dev`.

## 5) Routing on Vercel
- `infra/vercel.json` defines routes so `/api/*` requests are served by Django while everything else goes to Next.js.
- After deployment, verify:
  - `/api/health/` returns `ok` (Django healthcheck).
  - `/` serves the marketing landing page.

## 6) Post-deploy checks
- Confirm environment variables are set in production.
- Create a trainer and user account (once auth is implemented) and exercise navigation.
- Wire database to Vercel Postgres/Neon and run migrations before live traffic.
