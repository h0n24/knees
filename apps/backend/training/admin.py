from datetime import date, timedelta

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
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
    generate_daily_exercises_for_day,
    generate_exercise_logs_for_all_users,
    generate_fatigue_logs_for_all_users,
    generate_recovery_logs_for_all_users,
)


User = get_user_model()


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
    selected_user_id = request.POST.get("user_id")
    target_user = None

    if selected_user_id:
        try:
            target_user = User.objects.get(pk=selected_user_id)
        except User.DoesNotExist:
            messages.error(request, "Selected user was not found; no data generated.")
            return redirect(request.path)

    if request.method == "POST":
        action = request.POST.get("action")
        scope = f"user {target_user.username}" if target_user else "all users"

        if action in {"delete_exercises", "delete_recovery", "delete_fatigue", "delete_all"}:
            day = request.POST.get("day")
            try:
                selected_day = date.fromisoformat(day)
            except (TypeError, ValueError):
                messages.error(request, "Select a valid day to reset data.")
                return redirect(request.path)

            daily_exercises_qs = DailyExercise.objects.filter(scheduled_for=selected_day)
            exercise_logs_qs = ExerciseLog.objects.filter(daily_exercise__scheduled_for=selected_day)
            recovery_logs_qs = RecoveryLog.objects.filter(recorded_for=selected_day)
            fatigue_logs_qs = FatigueLog.objects.filter(recorded_for=selected_day)

            if target_user:
                daily_exercises_qs = daily_exercises_qs.filter(user=target_user)
                exercise_logs_qs = exercise_logs_qs.filter(user=target_user)
                recovery_logs_qs = recovery_logs_qs.filter(user=target_user)
                fatigue_logs_qs = fatigue_logs_qs.filter(user=target_user)

            deleted_daily_exercises = deleted_exercise_logs = deleted_recovery_logs = (
                deleted_fatigue_logs
            ) = 0

            if action in {"delete_exercises", "delete_all"}:
                deleted_exercise_logs, _ = exercise_logs_qs.delete()
                deleted_daily_exercises, _ = daily_exercises_qs.delete()

            if action in {"delete_recovery", "delete_all"}:
                deleted_recovery_logs, _ = recovery_logs_qs.delete()

            if action in {"delete_fatigue", "delete_all"}:
                deleted_fatigue_logs, _ = fatigue_logs_qs.delete()

            messages.success(
                request,
                "Removed {exercises} exercises, {exercise_logs} exercise logs, {recovery}"
                " recovery logs, and {fatigue} fatigue logs for {scope} on {day}.".format(
                    exercises=deleted_daily_exercises,
                    exercise_logs=deleted_exercise_logs,
                    recovery=deleted_recovery_logs,
                    fatigue=deleted_fatigue_logs,
                    scope=scope,
                    day=selected_day,
                ),
            )

        elif action == "generate_daily_exercises":
            day = request.POST.get("day")
            try:
                selected_day = date.fromisoformat(day)
            except (TypeError, ValueError):
                messages.error(request, "Select a valid day to generate exercises.")
                return redirect(request.path)

            created = generate_daily_exercises_for_day(selected_day, user=target_user)
            messages.success(
                request,
                f"Generated {created} exercises for {scope} on {selected_day}.",
            )

        elif action == "recovery":
            created = generate_recovery_logs_for_all_users(user=target_user)
            messages.success(
                request,
                f"Generated {created} recovery logs for {scope} over the past 30 days.",
            )
        elif action == "fatigue":
            created = generate_fatigue_logs_for_all_users(user=target_user)
            messages.success(
                request,
                f"Generated {created} fatigue logs for {scope} over the past 30 days.",
            )
        elif action == "exercise":
            result = generate_exercise_logs_for_all_users(user=target_user)
            messages.success(
                request,
                "Generated {daily} scheduled exercises and {logs} exercise logs for "
                "{scope} 30 days ago.".format(scope=scope, **result),
            )
        elif action == "all":
            result = generate_all_account_test_data(user=target_user)
            messages.success(
                request,
                "Generated {recovery} recovery logs, {fatigue} fatigue logs, {daily} "
                "scheduled exercises, and {exercise_logs} exercise logs across "
                "{scope}.".format(scope=scope, **result),
            )
        else:
            messages.error(request, "Unknown action; no test data was generated.")
        return redirect(request.path)

    context = dict(
        admin.site.each_context(request),
        title="Account test data generators",
        users=User.objects.all(),
        selected_user_id=selected_user_id,
        day_options=[date.today() - timedelta(days=offset) for offset in range(0, 30)],
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
