from __future__ import annotations

import re
from datetime import timedelta

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.backend.training.models import RecoveryLog


class RecoveryLogForm(forms.ModelForm):
    sleep_duration = forms.CharField(label="Sleep Time")

    class Meta:
        model = RecoveryLog
        fields = ["sleep_duration", "sleep_quality", "nutrition", "comment"]
        widgets = {
            "sleep_quality": forms.NumberInput(
                attrs={
                    "min": 0,
                    "max": 100,
                    "placeholder": "Eg. 80",
                    "class": "rounded-2xl border border-transparent bg-white px-4 py-3 shadow-none focus-within:ring-2 focus-within:ring-transparent focus:outline-none focus:border-transparent",
                    "aria-describedby": "sleep-quality-help",
                }
            ),
            "nutrition": forms.Select(
                attrs={
                    "class": "w-full bg-transparent px-4 py-3 text-sm shadow-none font-semibold text-slate-900 focus:outline-none",
                }
            ),
            "comment": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Custom comment for the trainer",
                    "class": "mt-2 w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 placeholder:text-slate-400 shadow-sm focus:border-indigo-600 focus:outline-none focus:ring-2 focus:ring-indigo-600/30",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["sleep_duration"].widget.attrs.update(
            {
                "placeholder": "7:20",
                "class": "w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm focus-within:ring-2 focus-within:ring-indigo-600/30 max-w-80 focus:outline-none",
                "inputmode": "numeric",
                "aria-describedby": "sleep-duration-help",
            }
        )
        self.fields["sleep_quality"].label = "Sleep Quality"
        self.fields["nutrition"].label = "Nutrition"
        self.fields["comment"].label = "Custom Comment"

    def clean_sleep_duration(self):
        value = self.cleaned_data.get("sleep_duration")
        if value is None:
            raise ValidationError("Please enter your sleep time in hours and minutes.")

        value = value.strip()
        match = re.fullmatch(r"(\d{1,2}):(\d{2})", value)
        if not match:
            raise ValidationError("Use the format h:mm (for example 7:20).")

        hours = int(match.group(1))
        minutes = int(match.group(2))

        if minutes >= 60:
            raise ValidationError("Minutes must be between 0 and 59.")

        return timedelta(hours=hours, minutes=minutes)


class PlanEditorForm(forms.Form):
    user = forms.ModelChoiceField(
        label="Athlete",
        queryset=User.objects.none(),
        help_text="Choose whose plan you want to adjust.",
    )
    start_date = forms.DateField(
        label="Week start",
        initial=timezone.localdate,
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "mt-1 h-10 w-full rounded-2xl bg-white px-3 text-sm ring-1 ring-zinc-200 focus:outline-none focus:ring-2 focus:ring-indigo-600",
            }
        ),
    )
    replace_existing = forms.BooleanField(
        label="Replace existing entries",
        required=False,
        help_text="If checked, overwrite any exercises already scheduled for that week.",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.order_by("username")


class FatigueAssessmentForm(forms.Form):
    def __init__(self, *args, questions: list[dict] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        questions = questions or []

        for question in questions:
            self.fields[question["field_name"]] = forms.IntegerField(
                min_value=1,
                max_value=5,
                initial=1,
                widget=forms.NumberInput(
                    attrs={
                        "type": "range",
                        "class": "fas-slider",
                        "min": 1,
                        "max": 5,
                        "step": 1,
                        "aria-label": question["text"],
                    }
                ),
            )
