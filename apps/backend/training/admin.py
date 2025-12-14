from django.contrib import admin

from apps.backend.training.models import DailyExercise, Exercise


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name", "difficulty_range", "external_id", "category_list")
    list_filter = ("difficulty_min", "categories")
    search_fields = ("name", "notes")

    @admin.display(description="Categories")
    def category_list(self, obj: Exercise) -> str:
        return ", ".join(obj.categories)


@admin.register(DailyExercise)
class DailyExerciseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "exercise",
        "exercise_difficulty",
        "scheduled_for",
        "order",
    )
    list_filter = ("scheduled_for", "user", "exercise__categories")
    search_fields = ("exercise__name", "user__username")
    ordering = ("-scheduled_for", "user", "order")
    autocomplete_fields = ("user", "exercise")
    date_hierarchy = "scheduled_for"

    @admin.display(description="Difficulty")
    def exercise_difficulty(self, obj: DailyExercise) -> str:
        return obj.exercise.difficulty_range
