from datetime import date

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from apps.backend.training.models import DailyExercise
from apps.backend.training.services import create_weekly_plan_for_user


class TrainingPlanTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="complex-pass-123")

    def test_weekly_plan_created_and_capped(self):
        created = create_weekly_plan_for_user(self.user)
        self.assertEqual(len(created), 35)

        today = date.today()
        todays_plan = DailyExercise.objects.filter(user=self.user, scheduled_for=today)
        self.assertEqual(todays_plan.count(), 5)
        total_difficulty = sum(item.exercise.difficulty_max for item in todays_plan)
        self.assertLessEqual(total_difficulty, 10)

    def test_health_page_lists_todays_exercises(self):
        create_weekly_plan_for_user(self.user)
        client = Client()
        client.force_login(self.user)

        response = client.get(reverse("health"))
        self.assertContains(response, "Today's plan")

        todays_plan = DailyExercise.for_today(self.user)
        for item in todays_plan:
            self.assertContains(response, item.exercise.name)

    def test_daily_exercises_store_minimum_prescription(self):
        create_weekly_plan_for_user(self.user)

        todays_plan = DailyExercise.for_today(self.user)

        for item in todays_plan:
            prescription = item.exercise.prescription or {}
            expected_sets = (prescription.get("sets") or {}).get("min")
            expected_reps = (prescription.get("reps") or {}).get("min")

            self.assertEqual(item.sets, expected_sets)
            self.assertEqual(item.repetitions, expected_reps)
