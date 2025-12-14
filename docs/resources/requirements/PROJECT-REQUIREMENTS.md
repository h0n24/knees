# Requirements — Knee Training Tracker (Combined)

This document combines:

- **Project requirements** for the Knee Training Tracker
- **Course requirements** for the Django final project (STEP IT Academy)

It is written as a single checklist-style reference for implementation and presentation.

---

## 1) Project overview

A Django web app for:

- **Users:** daily knee training + quick recovery check-in + motivation
- **Trainers/Admins:** oversight dashboards, reports, and plan editing (including approving/overriding weekly auto-progression)

Non-medical note: this is a habit tracker and educational project. No diagnosis, no treatment promises.

---

## 2) Core user experiences

### 2.1 User daily flow

- View **Today’s plan** (exercises + prescription)
- Log completion quickly (done / partial + optional note)
- Fill **Daily Check-in**:
  - sleep hours
  - optional sleep score
  - simple nutrition prompts
  - simplified fatigue input (4 questions → auto score 0–10)
  - manual fatigue override (0–10)
- Receive a short **motivational message** after logging

### 2.2 Trainer/Admin flow

- Overview dashboard: adherence, fatigue level, trends
- Reports:
  - daily
  - weekly
  - monthly
- Training plan editor:
  - edit plan items
  - approve/override auto-progression suggestion

### 2.3 Authentication + roles

- Registration / login / logout
- Role-aware navigation:
  - USER vs TRAINER/ADMIN
- Authorization:
  - users can only access their own data
  - trainers/admins can access assigned users

---

## 3) Data + logic requirements

### 3.1 Data collected

**Training**

- planned items (from plan)
- completion status
- optional note

**Recovery / regeneration signals (simple)**

- sleep hours
- optional sleep score
- nutrition prompts (minimal)
- fatigue questionnaire (4 answers)
- fatigue score 0–10 (auto + final)

### 3.2 Rules / automation

**Weekly auto-progression (explainable)**

- Generate a next-week plan suggestion using:
  - adherence rate
  - average fatigue
  - fatigue trend
- Trainer can accept or modify

### 3.3 Validation & integrity

- Server-side validation (Django forms / validators)
- Prevent duplicate check-ins (unique per user + date)
- Safe defaults

---

## 4) UX + UI requirements

- Mobile-first, calming, bright UI
- Readable typography (≥16px)
- Low-friction forms (few fields, good defaults)
- Clear states: empty / loading / error
- Accessible baseline: keyboard navigable, sensible contrast

---

## 5) Course requirements checklist (must-have)

### 5.1 Functional

- ✅ User registration + login (auth + authorization)
- ✅ At least one **data input form** (Daily Check-in)
- ✅ At least one **data table view** (logs / reports)
  - sorting + filtering recommended
- ✅ Database (SQLite allowed)

### 5.2 Interface

- ✅ Main menu with links to key pages
- ✅ About page (what it is + who built it)
- ✅ Footer:
  - copyright
  - privacy policy link

### 5.3 Technical

- ✅ Django framework
- ✅ Python best practices / clean code

---

## 6) Optional features (course points)

- Better UI (professional templates, responsive)
- Deployment to hosting + SSL (Let’s Encrypt or equivalent)
- Interactive JS components (e.g., DataTables)

---

## 7) Evaluation summary (course)

- Basic requirements working + presentation requirements met: **5 points (pass)**
- Deployment + SSL: +2
- Professional templates: +2
- JS components: +1
- Maximum: **10 points**

---

## 8) Presentation requirements (5-minute scenario)

Presentation should include:

- About the author
- Tech stack (Python, Django, frontend)
- Short project description
- Goals + whether it could be used in real life
- Target audience
- Commercial value (basic estimate)
- A short live demo:
  - registration/login
  - core functionality
  - show menu pages
  - show mobile view via Chrome dev tools

---

## 9) Deliverables to keep in-repo

- `README.md` (product overview + architecture)
- `CREATIVE_BRIEF.md` (tone + visual direction)
- `EXERCISES.md` / `exercises.json` (exercise library)
- `REQUIREMENTS.md` (this file)
- `PRIVACY_POLICY.md` (or a dedicated page)
- Wireframes/screenshots (optional): `wireframes/`

---

## 10) Definition of done (MVP)

A reviewer can:

1. Register and log in
2. See Today’s plan
3. Mark training as completed
4. Submit a Daily Check-in (sleep, nutrition prompts, fatigue → score)
5. See logged entries in a table
6. Open Trainer/Admin dashboard (with a trainer account) and view:
   - adherence and fatigue summaries
   - daily/weekly/monthly report pages
   - plan editor with an auto-progression suggestion
7. Navigate via the main menu
8. Open About page
9. See footer with privacy policy link
