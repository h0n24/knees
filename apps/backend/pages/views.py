from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.backend.training.models import DailyExercise
from apps.backend.training.services import create_weekly_plan_for_user


def landing_page(request):
    return render(
        request,
        "pages/landing.html",
        {
            "title": "Knee Training Tracker",
            "description": "Stay on track with daily training and quick recovery check-ins.",
        },
    )


@login_required
def health_page(request):
    todays_exercises_qs = DailyExercise.objects.filter(
        user=request.user, scheduled_for=timezone.localdate()
    )

    if not todays_exercises_qs.exists():
        create_weekly_plan_for_user(request.user)
        todays_exercises_qs = DailyExercise.objects.filter(
            user=request.user, scheduled_for=timezone.localdate()
        )

    todays_exercises = todays_exercises_qs.select_related("exercise").order_by(
        "order", "id"
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
