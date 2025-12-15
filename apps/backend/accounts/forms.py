from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": (
                    "block w-full rounded-md border-0 bg-slate-50 px-4 py-3 "
                    "text-slate-900 shadow-sm ring-1 ring-inset ring-slate-200 "
                    "placeholder:text-slate-400 placeholder:text-sm focus:ring-2 "
                    "focus:ring-inset focus:ring-indigo-600"
                ),
                "placeholder": "Write your username, without space and special characters",
                "autocomplete": "username",
            }
        )

        self.fields["email"].widget.attrs.update(
            {
                "class": (
                    "block w-full rounded-md border-0 bg-slate-50 px-4 py-3 text-slate-900 "
                    "shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 "
                    "placeholder:text-sm focus:ring-2 focus:ring-inset focus:ring-indigo-600"
                ),
                "placeholder": "Write your email",
                "autocomplete": "email",
            }
        )

        password_classes = (
            "block w-full rounded-md border-0 bg-slate-50 px-4 py-3 pr-12 text-slate-900 "
            "shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 placeholder:text-sm "
            "focus:ring-2 focus:ring-inset focus:ring-indigo-600"
        )

        self.fields["password1"].widget.attrs.update(
            {
                "class": password_classes,
                "placeholder": "Write your password, longer is better. 8 chars is minimum",
            }
        )

        self.fields["password2"].widget.attrs.update(
            {
                "class": password_classes,
                "placeholder": "Make sure you remember them",
            }
        )

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].widget.attrs.update(
            {
                "class": (
                    "block w-full rounded-md border-0 bg-slate-50 px-4 py-3 text-slate-900 "
                    "shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 placeholder:text-sm "
                    "focus:ring-2 focus:ring-inset focus:ring-indigo-600"
                ),
                "placeholder": "Your username or email",
                "autocomplete": "username",
            }
        )

        self.fields["password"].widget.attrs.update(
            {
                "class": (
                    "block w-full rounded-md border-0 bg-slate-50 px-4 py-3 pr-12 text-slate-900 "
                    "shadow-sm ring-1 ring-inset ring-slate-200 placeholder:text-slate-400 placeholder:text-sm "
                    "focus:ring-2 focus:ring-inset focus:ring-indigo-600"
                ),
                "placeholder": "Your password",
            }
        )


class UserSettingsForm(forms.ModelForm):
    password1 = forms.CharField(
        label="New password", widget=forms.PasswordInput, required=False
    )
    password2 = forms.CharField(
        label="Confirm new password", widget=forms.PasswordInput, required=False
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name")

    def __init__(self, user: User, *args, **kwargs):
        kwargs.setdefault("instance", user)
        super().__init__(*args, **kwargs)
        self.user = user or self.instance

        input_classes = (
            "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm "
            "text-slate-900 shadow-sm focus:border-indigo-600 focus:outline-none "
            "focus:ring-2 focus:ring-indigo-600/30"
        )

        for field_name in ("username", "first_name", "last_name", "password1", "password2"):
            self.fields[field_name].widget.attrs.update({"class": input_classes})

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")
            validate_password(password1, self.instance)

        return cleaned_data

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")

        if password1:
            user.set_password(password1)

        if commit:
            user.save()

        return user
