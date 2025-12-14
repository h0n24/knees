from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class PageAccessTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="basic user")
        Group.objects.get_or_create(name="trainer user")

    def _create_user(self, username: str, group_name: str) -> User:
        user = User.objects.create_user(username=username, password="pass12345")
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return user

    def test_basic_user_redirected_from_trainer_page(self):
        user = self._create_user("basic", "basic user")
        self.client.force_login(user)

        response = self.client.get(reverse("trainer"))

        self.assertRedirects(response, reverse("health"))

    def test_trainer_user_can_view_trainer_page(self):
        user = self._create_user("trainer", "trainer user")
        self.client.force_login(user)

        response = self.client.get(reverse("trainer"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Trainer portal")

    def test_trainer_user_can_access_health_page(self):
        user = self._create_user("trainer", "trainer user")
        self.client.force_login(user)

        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)

    def test_anonymous_users_are_redirected_to_login_for_health_page(self):
        response = self.client.get(reverse("health"))

        login_url = reverse("login")
        expected_url = f"{login_url}?next={reverse('health')}"
        self.assertRedirects(response, expected_url)
