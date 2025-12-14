from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from apps.backend.accounts.forms import RegisterForm


def login_page(request):
    return render(
        request,
        "accounts/login.html",
        {"title": "Login", "cta": "Welcome back"},
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
