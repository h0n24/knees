from __future__ import annotations

from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Exercise(models.Model):
    external_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    difficulty_min = models.PositiveSmallIntegerField()
    difficulty_max = models.PositiveSmallIntegerField()
    categories = models.JSONField(default=list)
    prescription = models.JSONField(default=dict)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Exercise"
        verbose_name_plural = "Exercises"

    def __str__(self) -> str:
        return self.name

    @property
    def difficulty_range(self) -> str:
        if self.difficulty_min == self.difficulty_max:
            return str(self.difficulty_min)
        return f"{self.difficulty_min}-{self.difficulty_max}"


class DailyExercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_exercises")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name="scheduled_instances")
    scheduled_for = models.DateField()
    order = models.PositiveSmallIntegerField(default=0)
    sets = models.PositiveSmallIntegerField(null=True, blank=True)
    repetitions = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheduled_for", "order", "id"]
        verbose_name = "Daily exercise"
        verbose_name_plural = "Daily exercises"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "scheduled_for", "order"],
                name="unique_daily_exercise_order",
            )
        ]

    def __str__(self) -> str:
        return f"{self.scheduled_for}: {self.exercise.name} for {self.user.username}"

    @property
    def difficulty_cap(self) -> int:
        return self.exercise.difficulty_max

    @classmethod
    def for_today(cls, user: User):
        return cls.objects.filter(user=user, scheduled_for=timezone.localdate()).select_related("exercise")

    def is_today(self) -> bool:
        return self.scheduled_for == timezone.localdate()

    def is_future(self) -> bool:
        return self.scheduled_for > timezone.localdate()

    def scheduled_day_display(self) -> str:
        return self.scheduled_for.strftime(settings.DATE_FORMAT if hasattr(settings, "DATE_FORMAT") else "%Y-%m-%d")


class ExerciseLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exercise_logs")
    daily_exercise = models.ForeignKey(
        DailyExercise, on_delete=models.CASCADE, related_name="logs"
    )
    set_number = models.PositiveSmallIntegerField()
    duration_seconds = models.PositiveIntegerField()
    started_at = models.DateTimeField()
    completed_at = models.DateTimeField()

    class Meta:
        ordering = ["completed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "daily_exercise", "set_number"],
                name="unique_exercise_log_per_set",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.daily_exercise.exercise.name} set {self.set_number} for {self.user.username}"
        )


class RecoveryLog(models.Model):
    class NutritionQuality(models.TextChoices):
        BELOW_AVERAGE = "below_average", "Below average"
        AVERAGE = "average", "Average"
        AMAZING = "amazing", "Amazing"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recovery_logs")
    recorded_for = models.DateField(default=timezone.localdate)
    sleep_duration = models.DurationField()
    sleep_quality = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    nutrition = models.CharField(
        max_length=20, choices=NutritionQuality.choices, default=NutritionQuality.AVERAGE
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recorded_for", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recorded_for"],
                name="unique_recovery_log_per_day",
            )
        ]
        verbose_name = "Recovery log"
        verbose_name_plural = "Recovery logs"

    def __str__(self) -> str:
        return f"Recovery log for {self.user.username} on {self.recorded_for}"
