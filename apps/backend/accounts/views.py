from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from apps.backend.accounts.forms import RegisterForm


def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request=request, data=request.POST)
    else:
        form = AuthenticationForm(request=request)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        if user.groups.filter(name="trainer user").exists():
            return redirect("trainer")
        return redirect("health")

    return render(
        request,
        "accounts/login.html",
        {"title": "Login", "cta": "Welcome back", "form": form},
    )


def register_page(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            basic_group, _ = Group.objects.get_or_create(name="basic user")
            user.groups.add(basic_group)
            return redirect("login")
    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "title": "Create your account",
            "cta": "Join the program and start tracking your knees.",
            "form": form,
        },
    )


def logout_page(request):
    return render(
        request,
        "accounts/logout.html",
        {
            "title": "Signed out",
            "message": "You have been logged out. Come back when you're ready to train again.",
        },
    )
