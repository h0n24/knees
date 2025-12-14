from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.backend.training.models import (
    DailyExercise,
    Exercise,
    ExerciseLog,
    FatigueLog,
    RecoveryLog,
)


class HealthTaskListTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user("bob", password="complex-pass-123")
        self.client.force_login(self.user)

    def _create_daily_exercise(self, *, sets=1) -> DailyExercise:
        exercise = Exercise.objects.create(
            external_id=999,
            name="Quad Stretch",
            difficulty_min=1,
            difficulty_max=2,
            categories=[],
            prescription={},
            notes="",
        )
        return DailyExercise.objects.create(
            user=self.user,
            exercise=exercise,
            scheduled_for=timezone.localdate(),
            order=1,
            sets=sets,
            repetitions=10,
        )

    def test_optional_labels_hidden_until_tasks_complete(self):
        self._create_daily_exercise()

        response = self.client.get(reverse("health"))
        self.assertNotContains(response, "sets completed")

        now = timezone.now()
        daily_exercise = DailyExercise.for_today(self.user).first()
        ExerciseLog.objects.create(
            user=self.user,
            daily_exercise=daily_exercise,
            set_number=1,
            duration_seconds=60,
            started_at=now,
            completed_at=now,
        )

        response = self.client.get(reverse("health"))
        self.assertContains(response, "1 sets completed")

    def test_sleep_and_nutrition_show_logged_details(self):
        sleep_duration = timedelta(hours=7, minutes=30)
        RecoveryLog.objects.create(
            user=self.user,
            recorded_for=timezone.localdate(),
            sleep_duration=sleep_duration,
            sleep_quality=85,
            nutrition=RecoveryLog.NutritionQuality.GREAT,
            comment="Feeling great",
        )

        response = self.client.get(reverse("health"))
        self.assertContains(response, "7:30")
        self.assertContains(response, "Great")

    def test_fatigue_score_scaled_and_translated(self):
        FatigueLog.objects.create(
            user=self.user,
            recorded_for=timezone.localdate(),
            responses=[],
            total_score=12,  # scaled to 24 because only 5 questions are used
        )

        response = self.client.get(reverse("health"))
        self.assertContains(response, "Mid-to-moderate fatigue")
