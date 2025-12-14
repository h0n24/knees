"""Project URL configuration for the skeleton build."""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path


def healthcheck(request):
    return HttpResponse("ok")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck, name="healthcheck"),
]
