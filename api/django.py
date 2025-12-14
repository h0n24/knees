"""Lightweight ASGI entrypoint for Vercel serverless functions."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apps.backend.config.settings")
application = get_asgi_application()
