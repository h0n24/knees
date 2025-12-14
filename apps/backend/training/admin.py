from django.contrib import admin

from apps.backend.training.models import DailyExercise, Exercise, ExerciseLog


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
