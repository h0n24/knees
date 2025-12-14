from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.backend.pages import views
from apps.backend.training.models import (
    DailyExercise,
    Exercise,
    ExerciseLog,
    FatigueLog,
    RecoveryLog,
)


class HealthCtaTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="basic user")
        Group.objects.get_or_create(name="trainer user")

        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.client.force_login(self.user)

    def _create_daily_exercise(self, name: str) -> DailyExercise:
        exercise = Exercise.objects.create(
            external_id=1,
            name=name,
            difficulty_min=1,
            difficulty_max=1,
            categories=[],
            prescription={},
        )
        return DailyExercise.objects.create(
            user=self.user,
            exercise=exercise,
            scheduled_for=timezone.localdate(),
            order=0,
            sets=1,
            repetitions=10,
        )

    def _complete_exercise(self, daily_exercise: DailyExercise) -> None:
        ExerciseLog.objects.create(
            user=self.user,
            daily_exercise=daily_exercise,
            set_number=1,
            duration_seconds=300,
            started_at=timezone.now() - timedelta(minutes=5),
            completed_at=timezone.now(),
        )

    def _create_recovery_log(self) -> RecoveryLog:
        return RecoveryLog.objects.create(
            user=self.user,
            recorded_for=timezone.localdate(),
            sleep_duration=timedelta(hours=6, minutes=30),
            sleep_quality=70,
            nutrition=RecoveryLog.NutritionQuality.OK,
            comment="Felt okay",
        )

    def _create_fatigue_log(self, responses_value: int = 2) -> FatigueLog:
        responses = [
            {
                "question_id": question["id"],
                "question": question["text"],
                "reversed": question["reversed"],
                "value": responses_value,
            }
            for question in views.FAS_QUESTIONS[:5]
        ]

        response_map = {
            f"question_{response['question_id']}": response["value"] for response in responses
        }
        questions = [
            {**response, "field_name": f"question_{response['question_id']}"}
            for response in responses
        ]
        total_score = views._calculate_fas_score(response_map, questions)

        return FatigueLog.objects.create(
            user=self.user,
            recorded_for=timezone.localdate(),
            responses=responses,
            total_score=total_score,
        )

    def test_health_cta_starts_when_session_not_begun(self):
        self._create_daily_exercise("Exercise 1")

        response = self.client.get(reverse("health"))

        self.assertContains(response, "Start today session")

    def test_health_cta_continues_when_session_started(self):
        daily = self._create_daily_exercise("Exercise 1")
        self._complete_exercise(daily)

        response = self.client.get(reverse("health"))

        self.assertContains(response, "Continue today session")

    def test_health_cta_updates_when_session_finished(self):
        daily = self._create_daily_exercise("Exercise 1")
        self._complete_exercise(daily)
        self._create_recovery_log()
        self._create_fatigue_log()

        response = self.client.get(reverse("health"))

        self.assertContains(response, "Update recovery and fatigue")
        self.assertContains(response, "edit_checkins=1")

    def test_finished_session_allows_checkin_updates(self):
        daily = self._create_daily_exercise("Exercise 1")
        self._complete_exercise(daily)
        self._create_recovery_log()
        fatigue_log = self._create_fatigue_log()

        session = self.client.session
        session["post_exercise_stage"] = 2
        session.save()

        response = self.client.get(reverse("exercise_session") + "?edit_checkins=1")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sleep &amp; nutrition check-in")
        self.assertContains(response, "6:30")

        response = self.client.post(
            reverse("exercise_session"),
            {
                "sleep_duration": "7:45",
                "sleep_quality": 85,
                "nutrition": RecoveryLog.NutritionQuality.GREAT,
                "comment": "Updated after reflection",
            },
            follow=True,
        )

        self.assertContains(response, "Fatigue Assessment")

        recovery_log = RecoveryLog.objects.get(user=self.user, recorded_for=timezone.localdate())
        self.assertEqual(recovery_log.sleep_quality, 85)
        self.assertEqual(recovery_log.nutrition, RecoveryLog.NutritionQuality.GREAT)
        self.assertEqual(recovery_log.comment, "Updated after reflection")
        self.assertEqual(recovery_log.sleep_duration, timedelta(hours=7, minutes=45))

        fatigue_payload = {
            f"question_{response['question_id']}": 4
            for response in fatigue_log.responses
        }

        response = self.client.post(reverse("exercise_session"), fatigue_payload, follow=True)

        self.assertContains(response, "All done for today")

        fatigue_log.refresh_from_db()
        self.assertTrue(all(entry["value"] == 4 for entry in fatigue_log.responses))

    def test_deleting_fatigue_log_reopens_checkins(self):
        daily = self._create_daily_exercise("Exercise 1")
        self._complete_exercise(daily)
        self._create_recovery_log()
        fatigue_log = self._create_fatigue_log()

        session = self.client.session
        session["post_exercise_stage"] = 2
        session.save()

        fatigue_log.delete()

        response = self.client.get(reverse("exercise_session"))

        self.assertContains(response, "Fatigue Assessment")
        self.assertEqual(self.client.session.get("post_exercise_stage"), 1)

    def test_deleting_recovery_log_reopens_checkins(self):
        daily = self._create_daily_exercise("Exercise 1")
        self._complete_exercise(daily)
        recovery_log = self._create_recovery_log()
        self._create_fatigue_log()

        session = self.client.session
        session["post_exercise_stage"] = 2
        session.save()

        recovery_log.delete()

        response = self.client.get(reverse("exercise_session"))

        self.assertContains(response, "Sleep &amp; nutrition check-in")
        self.assertEqual(self.client.session.get("post_exercise_stage"), 0)
