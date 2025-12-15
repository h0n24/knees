import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the admin user from environment variables."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_ADMIN_USER", "admin")
        password = os.getenv("DJANGO_ADMIN_PASSWORD")
        email = os.getenv("DJANGO_ADMIN_EMAIL", "admin@example.com")

        if not password:
            self.stdout.write(
                self.style.WARNING("DJANGO_ADMIN_PASSWORD not set; skipping admin creation")
            )
            return

        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email}
        )
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        action = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{action} admin user '{username}'"))
