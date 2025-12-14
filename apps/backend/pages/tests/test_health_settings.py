from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class HealthSettingsViewTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="basic user")
        self.user = User.objects.create_user(
            username="tester", password="initialpass123", first_name="Old", last_name="Name"
        )

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("health_settings"))
        login_url = reverse("login")
        expected_url = f"{login_url}?next={reverse('health_settings')}"
        self.assertRedirects(response, expected_url)

    def test_user_can_update_profile_fields(self):
        self.client.force_login(self.user)
        payload = {
            "username": "updatedtester",
            "first_name": "New",
            "last_name": "Name",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(reverse("health_settings"), payload)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "updatedtester")
        self.assertEqual(self.user.first_name, "New")

    def test_user_can_change_password_and_remain_authenticated(self):
        self.client.force_login(self.user)
        payload = {
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "password1": "newsecurepass456",
            "password2": "newsecurepass456",
        }

        response = self.client.post(reverse("health_settings"), payload)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newsecurepass456"))

        follow_up = self.client.get(reverse("health_settings"))
        self.assertEqual(follow_up.status_code, 200)
