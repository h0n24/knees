# Knee Training Tracker

A Django app for tracking daily knee work, quick recovery signals, and lightweight trainer oversight.

This repo is written as a **course-grade reference project**: modern, clean, and easy to understand.

> Medical note: this is **not** a medical device. It does not diagnose, treat, or prevent disease. Data is self-reported and meant for education and habit tracking.

---

## Why this exists

Many knee issues improve with **consistent, progressive training** plus **adequate recovery**. This app keeps the daily workflow short:

1) See today’s plan  
2) Do the session  
3) Log recovery + fatigue  
4) Get a simple progress view (and, for trainers, oversight)

It also serves as a clean base for future experiments (e.g., whether adherence + fatigue trends correlate with improved function).

---

## Who it’s for

**Athletes / users**
- want a fast daily loop
- want simple signals (sleep, nutrition, fatigue) without “forms hell”
- want visible progress over time

**Trainers / staff**
- want adherence + recovery trend overview
- want per-user drill-downs (today / 7d / 30d)
- want to generate and adjust a weekly plan using a shared exercise library

---

## Run locally (SQLite by default)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # optional, but needed for trainer/staff area
python manage.py runserver
```

> On Windows, activate with `.\.venv\Scriptsctivate` instead of `source .venv/bin/activate`.

---

## Seed data (exercise library)

The project includes an exercise library in `exercises.json`.

On first use of the Health / Trainer parts, the app ensures the exercise library is present so the demo flow works out of the box.

---

## What the app delivers

### Health area (`/health/`)
A guided daily flow for the signed-in user.

- **Today view**: shows today’s scheduled exercises and the “next step” CTA (start / continue / finish).
- **Exercise session** (`/health/exercise/`): walks through sets in order, logs time/duration, then collects:
  - recovery: `sleep_duration`, `sleep_quality`, `nutrition`, optional comments
  - fatigue: a **4-question** survey that computes a total score and stores structured responses
- **Progress dashboard** (`/health/progress/`): visualizes recent training + recovery trends (e.g., last 30 days).
- **Settings** (`/health/settings/`): account/profile basics.

### Trainer area (`/trainer/`)
Trainer routes require **staff** access or membership in the `trainer user` group.

- **People overview**: lists users with quick signals (plan count, adherence, latest fatigue, sleep, nutrition label).
- **User drill-down** (`/trainer/<username>/`):
  - report cards for **today / 7 days / 30 days**
  - upcoming 7-day plan view
  - recovery timeline (sleep / fatigue / nutrition balance)
  - tools to generate/replace a week plan starting on a chosen day, using the bundled exercise library and safe difficulty caps
- **Exercise library** (`/trainer/exercises/`): browse seeded movements (categories + difficulty ranges).
- **Navigation helpers**: remembers recently viewed athletes for faster switching.

---

## Data captured

**Training**
- scheduled plan items per day (ordered)
- per-set (or per-item) logging with timestamps and duration
- completion status and optional notes/comments

**Recovery (daily)**
- sleep duration
- sleep quality/score
- nutrition quality label/value
- optional comments
- enforced uniqueness per user/day

**Fatigue (daily)**
- 4 question answers stored as structured data (JSON)
- computed fatigue total score

---

## Auto-progression (weekly planning)

The weekly planner aims to be **simple and explainable**.

Typical inputs:
- adherence (done vs planned)
- recent fatigue average
- fatigue trend (rising / stable / falling)

Example rules of thumb:
- adherence ≥ 80% and fatigue ≤ 4 → nudge volume up (+5–10%)
- adherence < 60% or fatigue ≥ 7 → deload (-10–20%)
- otherwise → keep similar and focus on consistency

Trainer can accept the proposal, override it, or regenerate.

---

## Roles & permissions

- **User**: sees only their own health flow and history.
- **Trainer/staff**: can view assigned users and manage plans/reports.

---

## UI/UX principles

- fast daily loop: *today → session → check-in → progress*
- mobile-first layout
- readable defaults (no tiny text)
- low-friction forms (few fields, good defaults)
- calm visuals + positive reinforcement

---

## Tech stack

- **Backend:** Python + Django (auth, ORM, admin, server templates)
- **Frontend:** server-rendered templates + Tailwind styles + small JS/HTMX-friendly patterns
- **DB:** SQLite (dev/course), easy to swap later

---

## Project structure (high level)

- `apps/` – Django project + backend feature apps
- `templates/` – server templates
- `static/` – static assets
- `tests/` – tests for critical logic
- `exercises.json` – bundled exercise library seed

---

## Course requirement mapping (quick)

- Auth (register/login/logout) ✅
- At least one form ✅ (daily recovery/fatigue)
- At least one table view ✅ (trainer overviews/reports)
- DB ✅ (SQLite)
- Main navigation ✅
- Footer + policy link ✅

---

## Privacy note

The app stores only what it needs to run the flows:
- account identifier (username/email)
- daily self-reported metrics (sleep/nutrition/fatigue)
- training plan + completion logs

If you deploy this publicly, add a clear Privacy Policy that states what you collect, why you collect it, retention, and deletion process.

---

## License

Educational project.
