# Project Creative / Design Brief — Knee Training Tracker

A calming, bright web app for **daily knee training tracking** and **simple recovery check-ins**, with **trainer oversight** and **weekly auto-progression suggestions**.

---

## 1) What + Why

### What we are building
A web application with two experiences:
- **User section:** a lightweight daily flow — see today’s plan → do it → log it → quick recovery check → get a motivational message.
- **Trainer/Admin section:** oversight dashboards, reporting, and training plan editing.

### Why it matters
- People benefit from **consistent, progressive** training habits.
- We want to capture **simple self-reported signals** (sleep, nutrition prompts, fatigue) alongside training volume.
- This is a **foundation** for future research workflows (not a medical tool).

### Non‑medical disclaimer
This app is for education and habit tracking. It does not diagnose, treat, or provide medical advice.

---

## 2) Goals

### Product goals
1. Make daily logging **fast** (under 60 seconds after training).
2. Increase adherence via **calm motivation** (streaks + supportive microcopy).
3. Provide trainers a clear overview of:
   - adherence (planned vs done)
   - fatigue signals
   - trends and risks (rising fatigue)
4. Keep the system explainable: auto-progression rules should be **simple and visible**.

### Design goals
1. Calm and bright experience — “clean clinic meets friendly coach.”
2. Strong hierarchy, readable typography, no visual noise.
3. Consistent components, spacing, and shadows.

### Technical goals (course-quality)
1. Modern best practices, but **simple to understand**.
2. Clear separation of concerns, testable business rules.

---

## 3) Audience

### Primary: Users
- Want a simple routine without friction.
- Often on mobile.
- Value reassurance, clarity, and momentum.

### Secondary: Trainers/Admins
- Need rapid scanning for many users.
- Want reliable summaries, comparisons, and editable plans.

### Accessibility baseline
- Keyboard navigable.
- Readable text sizes (≥16px).
- Contrast safe for primary UI states.

---

## 4) Scope and Constraints

### Must have (MVP)
- Authentication and roles
- Today plan view
- Completion logging
- Daily check-in (sleep, nutrition prompts, fatigue)
- Motivational message after logging
- Trainer dashboards + daily/weekly/monthly reports
- Plan editor + ability to override auto-progression

### Nice to have
- Calendar heatmap
- Export CSV (trainer)
- “Notes” timeline per user

### Out of scope (for now)
- Medical claims, diagnoses, or rehab prescriptions
- Wearable API integrations
- Real-time chat

---

## 5) Simplified competition / strategy

This is an educational project, so we don’t compete on marketing.

What we *do* differentiate on:
- **Low friction daily flow** (less data, more consistency)
- **Calming UX** instead of “hardcore fitness dashboard”
- **Explainable progression rules** rather than opaque “AI coaching”

---

## 6) Value proposition / USP

1. **One-minute daily check-in** tied to actual training completion.
2. **Fatigue-aware progression** (simple rules, trainer override).
3. **Dual interface**: user simplicity + trainer depth.
4. **Motivational but not cringe** — supportive, calm, evidence-adjacent tone.

---

## 7) Tone of Voice

### Personality
- Calm, encouraging, respectful
- Clear and concise
- Science-adjacent (measured, humble)
- Never dramatic, never guilt-based

### Writing rules
- Short sentences. Strong verbs.
- Prefer neutral phrasing: “Notice / Track / Adjust.”
- Avoid absolutes (“always”, “guaranteed”, “cures”).

### Microcopy examples
- Completion:
  - “Nice work. Small steps add up.”
  - “Logged. Now recover well.”
- High fatigue:
  - “Noted. Today is a good day to keep it gentle.”
  - “Fatigue is up. Consider reducing volume.”
- Missed day:
  - “No problem. Restart with today.”

### Motivational content style
- 1–2 sentences max.
- Avoid hype. Prefer grounded encouragement.
- Optionally reference streaks:
  - “3-day streak. Keep it easy and consistent.”

---

## 8) Visual Direction

Inspired by **Tailwind UI ‘Salient’**: bright surfaces, blue-to-purple gradients, clean typography, soft shadows.

### Mood
- Bright, airy, calming
- “Morning light + gentle focus”

### Color system (suggested tokens)
Use a restrained palette:
- **Base:** white / near-white backgrounds
- **Primary:** bright blue
- **Accent:** purple/violet
- **Support:** slate neutrals

Suggested CSS variables:
```css
:root {
  --bg: #ffffff;
  --surface: #ffffff;
  --surface-2: #f8fafc;        /* slate-50 */
  --text: #0f172a;             /* slate-900 */
  --muted: #475569;            /* slate-600 */
  --border: #e2e8f0;           /* slate-200 */

  --primary: #2563eb;          /* blue-600 */
  --primary-2: #3b82f6;        /* blue-500 */
  --accent: #7c3aed;           /* violet-600 */

  --success: #16a34a;          /* green-600 */
  --warning: #f59e0b;          /* amber-500 */
  --danger: #ef4444;           /* red-500 */
}
```

### Gradients
- Use gradients only for **hero headers, banners, and subtle highlights**.
- Keep them soft (low saturation background glow).

Example:
```css
.hero-gradient {
  background:
    radial-gradient(900px 500px at 20% 10%, rgba(59,130,246,.25), transparent 60%),
    radial-gradient(900px 500px at 80% 20%, rgba(124,58,237,.20), transparent 60%),
    linear-gradient(to bottom, #ffffff, #f8fafc);
}
```

### Shadows and depth
- Prefer soft elevation, never harsh.

Example:
```css
.card {
  border: 1px solid var(--border);
  box-shadow: 0 1px 2px rgba(15,23,42,.06), 0 8px 24px rgba(15,23,42,.08);
  border-radius: 16px;
}
```

### Typography
- Use a clean sans serif.
- Large, readable defaults:
  - body: 16–18px
  - headings: clear hierarchy
- Line length: ~60–75 characters.

### Iconography
- Minimal line icons.
- Use icons as supportive cues (not decoration).

---

## 9) Layout and Component Guidelines

### Layout principles
- Mobile-first.
- Consistent spacing scale (e.g., 4/8/12/16/24/32).
- Prefer cards over heavy borders.

### Key components
- **Top nav** with role-aware links
- **Today card** (plan summary + CTA)
- **Plan item row** (exercise, prescription, completion)
- **Daily check-in card** (sleep + nutrition + fatigue)
- **Motivation toast/banner** after submit
- **Trainer tables** (filter/sort)
- **Report chips** (adherence %, fatigue avg)

### States
- Empty state:
  - “No plan for today yet. Ask your trainer or generate a starter plan.”
- Loading:
  - subtle skeletons
- Error:
  - one clear message + next action

---

## 10) User Experience Flows

### User daily flow
1. Open “Today”
2. Review plan (1 screen)
3. Mark completed (quick)
4. Daily check-in (sleep, nutrition prompts, fatigue)
5. Receive motivation message

### Trainer flow
1. Open dashboard
2. Scan risks (high fatigue, low adherence)
3. Open user detail
4. Review weekly/monthly trends
5. Adjust training plan or approve auto-progression

---

## 11) Content / Information Architecture

### User navigation
- Today
- Check-in
- History
- Profile
- About

### Trainer navigation
- Dashboard
- Users
- Reports
- Plans
- About

---

## 12) Success criteria

### MVP success
- Daily flow is usable on mobile without frustration.
- Trainers can identify:
  - users not training
  - users over-fatigued
- Reports are understandable without explanation.

### Metrics (simple)
- Adherence % over 7 / 30 days
- Streak length
- Average fatigue score
- % of days with completed check-in

---

## 13) Deliverables

- Creative brief (this document)
- Minimal design system (tokens + components)
- Key screens (wireframes or simple mockups)
- Implemented web app:
  - user daily flow
  - trainer reports and plan editor
- Short demo script

---

## 14) Implementation notes for design consistency

- Centralize tokens (CSS variables) and reuse.
- Use a component-like approach even in templates:
  - `templates/components/card.html`
  - `templates/components/button.html`
- Keep forms consistent:
  - label placement, help text, error style, spacing

---

## 15) “Do / Don’t” checklist

### Do
- Keep UI bright and calm
- Use gradients sparingly
- Encourage without guilt
- Make daily input fast

### Don’t
- Use aggressive gamification
- Use small text or dense tables without spacing
- Claim medical outcomes
- Hide next actions behind ambiguity

