from django.contrib.auth import get_user_model
from django.urls import reverse


def test_logout_logs_user_out(client):
    user_model = get_user_model()
    user = user_model.objects.create_user(username="logout_user", password="password123")

    client.force_login(user)
    response = client.get(reverse("logout"))

    assert response.wsgi_request.user.is_authenticated is False
