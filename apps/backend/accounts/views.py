from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render

from apps.backend.accounts.forms import RegisterForm


def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect("landing")
    else:
        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {
            "title": "Login",
            "cta": "Welcome back",
            "form": form,
        },
    )


def register_page(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. You can now log in.")
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
    logout(request)
    messages.info(request, "You have been logged out.")
    return render(
        request,
        "accounts/logout.html",
        {
            "title": "Signed out",
            "message": "You have been logged out. Come back when you're ready to train again.",
        },
    )
