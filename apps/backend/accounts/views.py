from django.shortcuts import render


def login_page(request):
    return render(
        request,
        "accounts/login.html",
        {"title": "Login", "cta": "Welcome back"},
    )


def register_page(request):
    return render(
        request,
        "accounts/register.html",
        {
            "title": "Create your account",
            "cta": "Join the program and start tracking your knees.",
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
