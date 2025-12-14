from __future__ import annotations

from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
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
