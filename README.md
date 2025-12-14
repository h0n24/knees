# Knee Training Tracker

A Django-based web app for **daily knee training**, **simple recovery tracking**, and **trainer oversight**.

This repository is intentionally written as a **course-grade reference project**: modern, clean, and easy to understand.

---

## 1. Why this app exists

Many knee issues improve with consistent, progressive training plus adequate recovery. This app provides a **minimal daily routine tracker** that also collects a few **lightweight recovery signals**.

It is a **basic layout for future research** into whether simple training habits correlate with improved knee function and (hypothetical) cartilage regeneration signals.

> Medical note: this is **not** a medical device and does not diagnose or treat conditions. Data is self‑reported and for educational purposes.

---

## 2. Target audiences

### A) Users (Daily Training)

People who want a **simple, non-obtrusive** daily workflow:

- See today’s knee routine
- Do it
- Log completion + quick recovery check
- Get a short motivational message

### B) Trainers / Admins

People who oversee a group:

- Monitor adherence and fatigue
- View daily / weekly / monthly reports
- Adjust training plans
- Review aggregated trends

---

## 3. Core product idea

A user does a small set of knee exercises daily. After the session they log:

- **Training volume** (auto from plan + completion)
- **Recovery signals** (sleep / nutrition / fatigue)

A trainer/admin can then:

- See how consistent the user is
- Detect rising fatigue
- Adjust the plan

The app also includes a simple weekly **auto‑progression** engine that proposes the next week’s volume based on past adherence and fatigue.

---

## 4. Feature list

### 4.1 User section (daily)

- **Authentication** (register/login/logout)
- **Today view**
  - today’s plan (exercises + sets/reps/time)
  - one-click “Mark done”
- **Daily check-in** form
  - sleep duration (hours)
  - sleep score (optional)
  - nutrition prompts (simple yes/no or 1–5)
  - simplified fatigue questionnaire (4 questions)
  - fatigue score output (0–10) + manual override
- **Motivation** after completion
  - short quote / micro‑speech
  - optionally tailored by streak or fatigue
- **History**
  - calendar / list of past days
  - streaks and adherence summary

### 4.2 Trainer/admin section

- **User overview dashboard**
  - adherence, streak, fatigue trend, planned vs done
- **Reports**
  - daily report (today)
  - weekly report (last 7 days)
  - monthly report (last 30 days)
- **Training plan editor**
  - modify plan items for a user or group
  - accept/reject proposed auto‑progression
- **Data tables**
  - sortable/filterable tables for check-ins and training logs

---

## 5. Daily data collected

### 5.1 Training

- planned exercises and volume (from plan)
- completion status
- optional notes (short text)

### 5.2 Recovery signals

Kept intentionally small and quick:

- **Sleep time** (hours)
- **Sleep score** (optional; user can input, e.g., from a tracker)
- **Nutrition prompts** (minimal)
  - example: “Protein adequate today?” (yes/no)
  - example: “Hydration OK?” (yes/no)
- **Simplified FAS (4 items)**
  - 4 short questions answered as 0–4 or 1–5
  - combined into **fatigue score 0–10**
  - user can manually override the final 0–10 score

---

## 6. Auto‑progression (weekly)

Goal: generate a **suggested plan for next week**.

Inputs (per user):

- adherence rate (done / planned)
- recent fatigue average (0–10)
- fatigue trend (rising / stable / falling)

Example rules (simple and explainable):

- If adherence ≥ 80% and fatigue ≤ 4 → increase volume slightly (+5–10%)
- If adherence < 60% or fatigue ≥ 7 → reduce volume (-10–20%)
- Else → keep similar

Trainer can:

- approve the suggestion
- adjust it manually

---

## 7. UI/UX principles

- **Fast daily flow**: today → done → check‑in → motivation
- **Mobile-first** responsive layout
- **No tiny text**: readable defaults (≥16px)
- **Low friction** forms: few fields, good defaults
- **Positive reinforcement**: streaks, clear progress, quotes

---

## 8. Tech stack

Backend:

- Python 3.x
- **Django** (auth, ORM, admin, forms, templates)

Frontend:

- HTML + CSS
- Vanilla JavaScript
- Optional UI framework: Bootstrap (or similar)
- Optional table UI: DataTables (or similar)

Database:

- SQLite (dev + course delivery)

---

## 9. Architecture overview

### 9.1 Django apps (suggested)

- `accounts` — registration/login/profile
- `training` — plans, exercises, completions
- `checkins` — daily recovery/fatigue entries
- `reports` — aggregation + dashboards
- `pages` — About, Privacy Policy

### 9.2 Core models (suggested)

- `UserProfile`
  - user, role (USER / TRAINER / ADMIN)
- `Exercise`
  - name, description, media_url (optional)
- `TrainingPlan`
  - owner (user or group), week_start, status (draft/active)
- `PlanItem`
  - plan, exercise, prescription (sets/reps/time), target_volume
- `TrainingLog`
  - user, date, plan_item, completed (bool), actual_volume, notes
- `DailyCheckIn`
  - user, date (unique per user)
  - sleep_hours, sleep_score (nullable)
  - nutrition flags
  - fas_q1..q4
  - fatigue_score_auto (0–10)
  - fatigue_score_final (0–10)

### 9.3 Permissions

- Normal users:
  - can view and edit only their own logs/check-ins
- Trainers/admin:
  - can view assigned users
  - can edit training plans

---

## 10. Key pages

Main navigation (example):

- Home / Today
- Check-in
- History
- Reports (trainer only)
- Plan editor (trainer only)
- About
- Privacy Policy

Footer:

- copyright
- Privacy Policy link

---

## 11. Validation and data quality

- Server-side validation with Django forms/model validators
- Client-side quality-of-life checks (JS), never as the only validation
- Prevent duplicate daily entries: `unique_together (user, date)`
- Clear error messages and safe defaults

---

## 12. Security and privacy

- Use Django authentication, CSRF protection, and secure password storage
- Role-based authorization for trainer/admin features
- Minimal personal data:
  - username/email for login
  - self-reported daily metrics only
- Provide a clear **Privacy Policy** page describing:
  - what is collected
  - why it is collected
  - retention policy
  - how to request deletion (if applicable)

---

## 13. Development quality bar

This is intended to be “state of the art but understandable”:

- PEP 8
- Type hints where helpful
- Small functions, clear naming
- Docstrings on non-trivial logic
- DRY templates (base layout)
- Consistent UI components
- Tests for critical logic (e.g., auto‑progression)

---

## 14. Project structure

Defined in Structure_Plan.md in the docs.

---

## 15. Reporting: definitions

- **Adherence %** = completed plan items / planned items
- **Load (simple)** = sum of (prescribed volume) or (actual volume)
- **Fatigue avg** = mean of fatigue_score_final over a period
- **Trend** = compare last 3 days vs previous 3 days (simple slope)

---

## 19. License

Educational project.

# Project Milestones

## Milestone 1 — Project skeleton

This commit establishes the dual-stack skeleton referenced in the structure plan:

- **Backend (Django 5)**: `apps/backend` with project settings under `apps/backend/config`, ASGI entrypoint, and placeholder apps for accounts, training, check-ins, reports, and pages.
- **Frontend (Next.js App Router)**: `apps/frontend` with grouped route folders for marketing, auth, user, and trainer experiences, plus a simple landing page layout.

The project is intended for **local development** with Django and Next.js running side by side; there is no serverless or Vercel dependency.

Run locally:

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (in a second terminal)
cd apps/frontend
npm install
npm run dev
```

---

## All milestones

1. Project skeleton

- Django project + apps
- Base template + navigation + footer

2. Auth

- register/login/logout
- roles

3. User daily flow

- today plan view
- training log submission
- daily check-in form
- motivation message

4. Trainer flow

- user list
- reports
- plan editor

5. Polish

- responsive UI
- sortable/filterable tables
- deployment (optional)

---

## 17. Presentation checklist

For the 5-minute demo:

- Show registration/login
- Show today’s plan + logging
- Show check-in + fatigue score
- Show trainer report page
- Mention stack, goals, and target audience

---

## 18. Course requirement mapping (quick)

- Registration/Login ✅
- At least one data input form ✅ (Daily Check‑In)
- At least one data table view ✅ (Logs/Reports table)
- Database ✅ (SQLite)
- Main menu ✅
- About page ✅
- Footer + Privacy Policy link ✅

Optional (extra points):

- Professional templates (Bootstrap) ⬜
- Deployment + SSL ⬜
- Interactive JS tables (DataTables) ⬜

---
