from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


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
    return render(
        request,
        "pages/health.html",
        {
            "title": "Health Check",
            "headline": "Keep your own training on track.",
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
