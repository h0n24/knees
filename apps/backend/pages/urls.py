from django.urls import path

from apps.backend.pages import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("health/", views.health_page, name="health"),
    path("trainer/", views.trainer_page, name="trainer"),
    path("about/", views.about_page, name="about"),
    path("privacy/", views.privacy_page, name="privacy"),
]
