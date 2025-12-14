from django.contrib.auth.decorators import login_required
from datetime import datetime

from django.shortcuts import redirect, render
from django.utils import timezone

from apps.backend.training.models import DailyExercise, ExerciseLog
from apps.backend.training.services import ensure_training_tables_ready


def landing_page(request):
    return render(
        request,
        "pages/landing.html",
        {
            "title": "Knee Training Tracker",
            "description": "Stay on track with daily training and quick recovery check-ins.",
        },
    )


def about_page(request):
    return render(
        request,
        "pages/about.html",
        {
            "title": "About Knee Training Tracker",
            "description": "Learn how Knee Training Tracker supports your recovery goals with guided exercises and progress tracking.",
        },
    )


def privacy_page(request):
    return render(
        request,
        "pages/privacy.html",
        {
            "title": "Privacy policy",
            "description": "We only collect the information needed to keep your training plan on track.",
        },
    )


@login_required
def health_page(request):
    ensure_training_tables_ready()

    todays_exercises = (
        DailyExercise.objects.filter(
            user=request.user, scheduled_for=timezone.localdate()
        )
        .select_related("exercise")
        .order_by("order", "id")
    )

    return render(
        request,
        "pages/health.html",
        {
            "title": "Health Check",
            "headline": "Keep your own training on track.",
            "todays_exercises": todays_exercises,
        },
        status=200,
    )


def _build_exercise_steps(todays_exercises):
    exercises = list(todays_exercises)
    if not exercises:
        return []

    max_sets = max(item.sets or 1 for item in exercises)
    ordered_sets = []

    for set_number in range(1, max_sets + 1):
        for daily_exercise in exercises:
            sets = daily_exercise.sets or 1
            if set_number <= sets:
                ordered_sets.append({
                    "daily_exercise": daily_exercise,
                    "set_number": set_number,
                })

    return ordered_sets


@login_required
def exercise_session_page(request):
    ensure_training_tables_ready()

    todays_exercises = list(
        DailyExercise.objects.filter(
            user=request.user, scheduled_for=timezone.localdate()
        ).select_related("exercise")
    )

    exercise_steps = _build_exercise_steps(todays_exercises)
    total_steps = len(exercise_steps) + 2  # sleep/nutrition + fatigue

    completed_logs = ExerciseLog.objects.filter(
        user=request.user, daily_exercise__in=[step["daily_exercise"] for step in exercise_steps]
    ).count()
    completed_logs = min(completed_logs, len(exercise_steps))

    post_exercise_stage = int(request.session.get("post_exercise_stage", 0) or 0)
    if completed_logs < len(exercise_steps):
        post_exercise_stage = 0

    completed_steps = completed_logs + min(post_exercise_stage, 2)
    current_step_number = min(completed_steps + 1, total_steps)
    progress_percent = (completed_steps / total_steps) * 100 if total_steps else 0

    current_timestamp = timezone.now()
    session_started_at = request.session.get("current_step_started_at")
    if session_started_at is None:
        request.session["current_step_started_at"] = current_timestamp.timestamp()
        session_started_at = request.session["current_step_started_at"]
    else:
        session_started_at = float(session_started_at)

    if request.method == "POST":
        started_at = datetime.fromtimestamp(session_started_at, tz=timezone.get_current_timezone())
        duration_seconds = max(int(current_timestamp.timestamp() - session_started_at), 1)

        if completed_logs < len(exercise_steps):
            current_step = exercise_steps[completed_logs]
            ExerciseLog.objects.update_or_create(
                user=request.user,
                daily_exercise=current_step["daily_exercise"],
                set_number=current_step["set_number"],
                defaults={
                    "duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "completed_at": current_timestamp,
                },
            )
            request.session["post_exercise_stage"] = 0
        else:
            post_exercise_stage = min(post_exercise_stage + 1, 2)
            request.session["post_exercise_stage"] = post_exercise_stage

        request.session["current_step_started_at"] = timezone.now().timestamp()
        return redirect("exercise_session")

    context = {
        "title": "Exercise session",
        "headline": "Work through today\'s plan one set at a time.",
        "steps": exercise_steps,
        "current_step": exercise_steps[completed_logs] if completed_logs < len(exercise_steps) else None,
        "current_set_number": exercise_steps[completed_logs]["set_number"] if completed_logs < len(exercise_steps) else None,
        "total_steps": total_steps,
        "current_step_number": current_step_number,
        "progress_percent": progress_percent,
        "post_exercise_stage": post_exercise_stage,
    }

    return render(request, "pages/exercise_session.html", context)


@login_required
def trainer_page(request):
    if not request.user.groups.filter(name="trainer user").exists():
        return redirect("health")

    return render(
        request,
        "pages/trainer.html",
        {
            "title": "Trainer portal",
            "description": "Oversight tools for monitoring adherence and adjusting plans.",
        },
    )
