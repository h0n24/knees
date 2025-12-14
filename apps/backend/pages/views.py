from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.backend.training.models import DailyExercise
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
