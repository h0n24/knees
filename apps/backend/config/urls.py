"""Project URL configuration for the skeleton build."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.backend.pages.urls")),
    path("auth/", include("apps.backend.accounts.urls")),
    path("admin/", admin.site.urls),
]
