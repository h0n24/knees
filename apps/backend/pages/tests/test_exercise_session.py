from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.backend.pages import views
from apps.backend.training.models import DailyExercise, Exercise, ExerciseLog


class ExerciseSessionTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="basic user")
        self.user = User.objects.create_user(username="tester", password="pass12345")
        self.client.force_login(self.user)

    def _create_daily_exercise(self, name: str, order: int, sets: int) -> DailyExercise:
        exercise = Exercise.objects.create(
            external_id=order + 1,
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
            order=order,
            sets=sets,
            repetitions=10,
        )

    def test_round_robin_ordering_of_sets(self):
        exercises = [
            self._create_daily_exercise("Exercise 1", 0, 2),
            self._create_daily_exercise("Exercise 2", 1, 2),
            self._create_daily_exercise("Exercise 3", 2, 1),
        ]

        ordered = views._build_exercise_steps(exercises)
        sequence = [
            (step["daily_exercise"].exercise.name, step["set_number"]) for step in ordered
        ]

        self.assertEqual(
            sequence,
            [
                ("Exercise 1", 1),
                ("Exercise 2", 1),
                ("Exercise 3", 1),
                ("Exercise 1", 2),
                ("Exercise 2", 2),
            ],
        )

    def test_logging_exercise_duration(self):
        daily = self._create_daily_exercise("Exercise 1", 0, 1)

        # Seed the session timer so we can calculate duration on POST.
        session = self.client.session
        session["current_step_started_at"] = timezone.now().timestamp() - 5
        session.save()

        response = self.client.post(reverse("exercise_session"))
        self.assertEqual(response.status_code, 302)

        log = ExerciseLog.objects.get(user=self.user, daily_exercise=daily)
        self.assertEqual(log.set_number, 1)
        self.assertGreaterEqual(log.duration_seconds, 1)
