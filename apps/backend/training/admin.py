from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path

from apps.backend.training.models import (
    DailyExercise,
    Exercise,
    ExerciseLog,
    FatigueLog,
    RecoveryLog,
)
from apps.backend.training.services import (
    generate_all_account_test_data,
    generate_exercise_logs_for_all_users,
    generate_fatigue_logs_for_all_users,
    generate_recovery_logs_for_all_users,
)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "difficulty_range", "external_id")
    list_filter = ("difficulty_min", "categories")
    search_fields = ("name", "notes")


@admin.register(DailyExercise)
class DailyExerciseAdmin(admin.ModelAdmin):
    list_display = ("user", "exercise", "scheduled_for", "order", "sets", "repetitions")
    list_filter = ("scheduled_for", "user")
    search_fields = ("exercise__name", "user__username")
    ordering = ("-scheduled_for", "user", "order")
    autocomplete_fields = ("user", "exercise")


@admin.register(ExerciseLog)
class ExerciseLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "daily_exercise",
        "set_number",
        "duration_seconds",
        "started_at",
        "completed_at",
    )
    list_filter = ("user", "daily_exercise")
    search_fields = ("daily_exercise__exercise__name", "user__username")
    ordering = ("-completed_at", "user", "daily_exercise")
    autocomplete_fields = ("user", "daily_exercise")


@admin.register(RecoveryLog)
class RecoveryLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recorded_for",
        "sleep_duration",
        "sleep_quality",
        "nutrition",
        "created_at",
    )
    list_filter = ("recorded_for", "nutrition", "user")
    search_fields = ("user__username", "comment")
    ordering = ("-recorded_for", "-created_at")
    autocomplete_fields = ("user",)


@admin.register(FatigueLog)
class FatigueLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "recorded_for",
        "total_score",
        "created_at",
    )
    list_filter = ("recorded_for", "user")
    search_fields = ("user__username",)
    ordering = ("-recorded_for", "-created_at")
    autocomplete_fields = ("user",)


def account_test_data_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "recovery":
            created = generate_recovery_logs_for_all_users()
            messages.success(
                request,
                f"Generated {created} recovery logs for all users over the past 30 days.",
            )
        elif action == "fatigue":
            created = generate_fatigue_logs_for_all_users()
            messages.success(
                request,
                f"Generated {created} fatigue logs for all users over the past 30 days.",
            )
        elif action == "exercise":
            result = generate_exercise_logs_for_all_users()
            messages.success(
                request,
                "Generated {daily} scheduled exercises and {logs} exercise logs for all "
                "users 30 days ago.".format(**result),
            )
        elif action == "all":
            result = generate_all_account_test_data()
            messages.success(
                request,
                "Generated {recovery} recovery logs, {fatigue} fatigue logs, {daily} "
                "scheduled exercises, and {exercise_logs} exercise logs across all "
                "users.".format(**result),
            )
        else:
            messages.error(request, "Unknown action; no test data was generated.")
        return redirect(request.path)

    context = dict(
        admin.site.each_context(request),
        title="Account test data generators",
        actions=[
            {
                "key": "recovery",
                "label": "Generate recovery logs",
                "description": "Creates 30 days of historical recovery logs for every account.",
                "primary": False,
            },
            {
                "key": "fatigue",
                "label": "Generate fatigue logs",
                "description": "Creates 30 days of historical fatigue logs for every account.",
                "primary": False,
            },
            {
                "key": "exercise",
                "label": "Generate exercise logs",
                "description": "Schedules daily exercises and logs their completion for the day 30 days ago.",
                "primary": False,
            },
            {
                "key": "all",
                "label": "Generate all test data",
                "description": "Runs all generators above to seed recovery, fatigue, and exercise logs.",
                "primary": True,
            },
        ],
    )
    return TemplateResponse(request, "admin/account_test_data.html", context)


def get_admin_urls(urls):
    def get_urls():
        extra = [
            path(
                "account-test-data/",
                admin.site.admin_view(account_test_data_view),
                name="account-test-data",
            ),
        ]
        return extra + urls

    return get_urls


admin.site.get_urls = get_admin_urls(admin.site.get_urls())
