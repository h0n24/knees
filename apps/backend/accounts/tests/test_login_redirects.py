from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class LoginRedirectTests(TestCase):
    def setUp(self):
        Group.objects.get_or_create(name="basic user")
        Group.objects.get_or_create(name="trainer user")

    def _create_user(self, username: str, group_name: str) -> User:
        user = User.objects.create_user(username=username, password="pass12345")
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        return user

    def test_basic_user_redirects_to_health(self):
        self._create_user("basic", "basic user")

        response = self.client.post(
            reverse("login"), {"username": "basic", "password": "pass12345"}
        )

        self.assertRedirects(response, reverse("health"))

    def test_trainer_user_redirects_to_trainer(self):
        self._create_user("trainer", "trainer user")

        response = self.client.post(
            reverse("login"), {"username": "trainer", "password": "pass12345"}
        )

        self.assertRedirects(response, reverse("trainer"))
