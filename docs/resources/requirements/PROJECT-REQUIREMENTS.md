# Project Requirements Snapshot

This document distills the primary functional and experience requirements for the Knee Training Tracker so they are easy to reference alongside the creative brief and wireframes.

## Core Experiences

- **User daily flow:** Today’s plan, quick completion logging, daily check-in (sleep, nutrition prompts, fatigue), and a short motivational message.
- **Trainer/Admin flow:** Dashboards to monitor adherence and fatigue, daily/weekly/monthly reports, and a training plan editor that can accept or override auto-progression suggestions.
- **Authentication and roles:** Registration/login/logout with role-aware navigation for users vs. trainers.

## Data + Logic

- **Training data:** Planned exercises and volume, completion status, and optional notes.
- **Recovery data:** Sleep hours/score, nutrition prompts, simplified four-question fatigue inputs that roll up to a 0–10 fatigue score with manual override.
- **Auto-progression:** Weekly suggestions based on adherence and fatigue trends (increase, hold, or decrease volume with trainer approval).
- **Validation and security:** Server-side validation, CSRF protection, role-based access, minimal personal data, and duplicate-prevention for daily entries.

## UX Principles

- Calm, bright, mobile-first UI with readable typography (≥16px), consistent spacing, and low-friction forms.
- Positive reinforcement (streaks, encouraging microcopy) without aggressive gamification.
- Clear empty/loading/error states and an accessible baseline (keyboard navigable, safe contrast).

## Deliverables to Track in Docs

- **Design tokens and component notes:** Colors, gradients, shadows, typography, and reusable card/button patterns.
- **Wireframes:** Desktop, mobile, and admin views stored in `../wireframes/`.
- **Privacy and About content:** Clear disclosure of data collected and purpose.
- **Demo guidance:** Quick flow for registration, daily logging, fatigue check, and trainer reporting.
