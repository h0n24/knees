from django.contrib import admin

from apps.backend.training.models import DailyExercise, Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "difficulty_range", "external_id")
    list_filter = ("difficulty_min", "categories")
    search_fields = ("name", "notes")


@admin.register(DailyExercise)
class DailyExerciseAdmin(admin.ModelAdmin):
    list_display = ("user", "exercise", "scheduled_for", "order")
    list_filter = ("scheduled_for", "user")
    search_fields = ("exercise__name", "user__username")
    ordering = ("-scheduled_for", "user", "order")
    autocomplete_fields = ("user", "exercise")
