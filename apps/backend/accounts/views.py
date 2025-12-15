from django.contrib.auth import login, logout
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from apps.backend.accounts.forms import LoginForm, RegisterForm
from apps.backend.training.services import create_weekly_plan_for_user


def _redirect_authenticated_user(user):
    if user.groups.filter(name="trainer user").exists():
        return redirect("trainer")
    return redirect("health")


def login_page(request):
    if request.user.is_authenticated:
        return _redirect_authenticated_user(request.user)

    data = request.POST if request.method == "POST" else None
    form = LoginForm(request=request, data=data)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return _redirect_authenticated_user(user)

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
            create_weekly_plan_for_user(user)
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
    if request.user.is_authenticated:
        logout(request)

    return render(
        request,
        "accounts/logout.html",
        {
            "title": "Signed out",
            "message": "You have been logged out. Come back when you're ready to train again.",
        },
    )
