from django.urls import path

from apps.backend.pages import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("health/", views.health_page, name="health"),
    path("health/progress/", views.health_progress_page, name="health_progress"),
    path("health/settings/", views.health_settings_page, name="health_settings"),
    path("health/exercise/", views.exercise_session_page, name="exercise_session"),
    path("trainer/exercises/", views.trainer_exercises_page, name="trainer_exercises"),
    path("trainer/<str:username>/", views.trainer_user_page, name="trainer_user"),
    path("trainer/", views.trainer_page, name="trainer"),
    path("about/", views.about_page, name="about"),
    path("privacy/", views.privacy_page, name="privacy"),
]
