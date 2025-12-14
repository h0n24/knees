from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


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
