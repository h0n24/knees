import random
from datetime import datetime, timedelta

from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from apps.backend.accounts.forms import UserSettingsForm
from apps.backend.pages.forms import FatigueAssessmentForm, PlanEditorForm, RecoveryLogForm
from apps.backend.training.models import DailyExercise, Exercise, ExerciseLog, FatigueLog, RecoveryLog
from apps.backend.training.services import create_weekly_plan_for_user, ensure_library_loaded, ensure_training_tables_ready


def landing_page(request):
    return render(
        request,
        "pages/landing.html",
        {
            "title": "Knee Training Tracker",
            "description": "Stay on track with daily training and quick recovery check-ins.",
        },
    )


def about_page(request):
    return render(
        request,
        "pages/about.html",
        {
            "title": "About Knee Training Tracker",
            "description": "Learn how Knee Training Tracker supports your recovery goals with guided exercises and progress tracking.",
        },
    )


def privacy_page(request):
    return render(
        request,
        "pages/privacy.html",
        {
            "title": "Privacy policy",
            "description": "We only collect the information needed to keep your training plan on track.",
        },
    )


def _user_is_trainer(user: User) -> bool:
    return user.is_staff or user.groups.filter(name="trainer user").exists()


def _record_recent_report(session, username: str) -> None:
    recent = session.get("trainer_recent_reports", [])

    if username not in recent:
        recent.insert(0, username)

    session["trainer_recent_reports"] = recent[:4]
    session.modified = True


def _trainer_navigation(*, request, selected: str, active_user: User | None = None) -> dict:
    recent_usernames = request.session.get("trainer_recent_reports", [])
    users = {
        user.username: user
        for user in User.objects.filter(username__in=recent_usernames)
    }

    recent_reports = []
    for username in recent_usernames:
        user = users.get(username)
        if not user:
            continue

        recent_reports.append(
            {
                "username": user.username,
                "name": user.get_full_name() or user.username,
                "url": reverse("trainer_user", args=[user.username]),
                "is_active": bool(active_user and user.username == active_user.username),
            }
        )

    return {
        "selected": selected,
        "recent_reports": recent_reports,
    }


@login_required
def trainer_user_page(request, username: str):
    if not _user_is_trainer(request.user):
        return redirect("health")

    ensure_training_tables_ready()
    ensure_library_loaded()

    athlete = get_object_or_404(User, username=username)
    _record_recent_report(request.session, athlete.username)
    plan_form = PlanEditorForm(request.POST or None, initial={"user": athlete})
    plan_form.fields["user"].queryset = User.objects.filter(id=athlete.id)
    plan_form.fields["user"].widget = plan_form.fields["user"].hidden_widget()

    plan_message = None
    if request.method == "POST" and plan_form.is_valid():
        start_date = plan_form.cleaned_data["start_date"]
        replace_existing = plan_form.cleaned_data["replace_existing"]
        created = create_weekly_plan_for_user(
            athlete, start_date=start_date, replace_existing=replace_existing
        )
        plan_message = {
            "user": athlete,
            "created": len(created),
            "start_date": start_date,
            "replace_existing": replace_existing,
        }

    context = {
        "title": f"{athlete.username} · Trainer",
        "headline": athlete.username,
        "plan_form": plan_form,
        "plan_message": plan_message,
        "reports": _trainer_reports(user=athlete),
        "summary": _trainer_summary_for_user(athlete),
        "upcoming_plan": _upcoming_plan_for_user(athlete),
        "trainer_nav": _trainer_navigation(
            request=request, selected="user_detail", active_user=athlete
        ),
    }

    return render(request, "pages/trainer_user_detail.html", context)


@login_required
def trainer_exercises_page(request):
    if not _user_is_trainer(request.user):
        return redirect("health")

    ensure_training_tables_ready()
    ensure_library_loaded()

    exercises = Exercise.objects.all()

    context = {
        "title": "Exercises · Trainer",
        "headline": "List of Exercises",
        "exercises": exercises,
        "trainer_nav": _trainer_navigation(request=request, selected="exercises"),
    }

    return render(request, "pages/trainer_exercises.html", context)


@login_required
def trainer_page(request):
    if not _user_is_trainer(request.user):
        return redirect("health")

    ensure_training_tables_ready()
    ensure_library_loaded()

    context = {
        "title": "Trainer",
        "headline": "Users",
        "people": _trainer_people(),
        "trainer_nav": _trainer_navigation(request=request, selected="users"),
    }

    return render(request, "pages/trainer_users.html", context)


@login_required
def health_page(request):
    ensure_training_tables_ready()

    todays_exercises = (
        DailyExercise.objects.filter(
            user=request.user, scheduled_for=timezone.localdate()
        )
        .select_related("exercise")
        .order_by("order", "id")
    )

    exercise_steps = _build_exercise_steps(todays_exercises)
    completed_exercise_logs = ExerciseLog.objects.filter(
        user=request.user, daily_exercise__in=[step["daily_exercise"] for step in exercise_steps]
    ).count()
    exercises_complete = bool(exercise_steps) and completed_exercise_logs >= len(exercise_steps)

    recovery_log = RecoveryLog.objects.filter(
        user=request.user, recorded_for=timezone.localdate()
    ).first()
    fatigue_log = FatigueLog.objects.filter(
        user=request.user, recorded_for=timezone.localdate()
    ).first()

    session_started = bool(completed_exercise_logs or recovery_log or fatigue_log)
    session_finished = bool(exercises_complete and recovery_log and fatigue_log)

    cta_label = "Start today session"
    cta_suffix = ""
    if session_finished:
        cta_label = "Update recovery and fatigue"
        cta_suffix = "?edit_checkins=1"
    elif session_started:
        cta_label = "Continue today session"

    sleep_label = _format_sleep_duration(recovery_log.sleep_duration) if recovery_log else None
    nutrition_label = recovery_log.get_nutrition_display() if recovery_log else None

    fatigue_label = None
    if fatigue_log:
        scaled_score = fatigue_log.total_score * 2
        if scaled_score <= 21:
            fatigue_label = "Normal/Healthy"
        elif scaled_score <= 34:
            fatigue_label = "Mid-to-moderate fatigue"
        else:
            fatigue_label = "Severe or extreme fatigue"

    tasks = [
        {
            "title": "Exercises",
            "complete": exercises_complete,
            "label": f"{len(exercise_steps)} sets completed" if exercises_complete else None,
        },
        {
            "title": "Sleep",
            "complete": bool(recovery_log),
            "label": sleep_label if recovery_log else None,
        },
        {
            "title": "Nutrition",
            "complete": bool(recovery_log),
            "label": nutrition_label if recovery_log else None,
        },
        {
            "title": "Fatigue",
            "complete": bool(fatigue_log),
            "label": fatigue_label,
        },
    ]

    return render(
        request,
        "pages/health.html",
        {
            "title": "Health Check",
            "headline": "Keep your own training on track.",
            "todays_exercises": todays_exercises,
            "tasks": tasks,
            "session_cta_label": cta_label,
            "session_cta_suffix": cta_suffix,
        },
        status=200,
    )


@login_required
def health_progress_page(request):
    ensure_training_tables_ready()

    end_date = timezone.localdate()
    start_date = end_date - timedelta(days=29)
    date_range = [start_date + timedelta(days=offset) for offset in range(30)]

    training_logs = ExerciseLog.objects.filter(
        user=request.user,
        completed_at__date__range=(start_date, end_date),
    ).values_list("completed_at", "duration_seconds")

    training_totals: dict = {}
    for completed_at, duration_seconds in training_logs:
        day = timezone.localtime(completed_at).date()
        training_totals[day] = training_totals.get(day, 0) + duration_seconds

    recovery_logs = RecoveryLog.objects.filter(
        user=request.user, recorded_for__range=(start_date, end_date)
    ).values_list("recorded_for", "sleep_duration")
    sleep_totals = {
        recorded_for: sleep_duration.total_seconds()
        for recorded_for, sleep_duration in recovery_logs
    }

    fatigue_logs = FatigueLog.objects.filter(
        user=request.user, recorded_for__range=(start_date, end_date)
    ).values_list("recorded_for", "total_score")
    fatigue_totals = {recorded_for: total_score for recorded_for, total_score in fatigue_logs}

    labels = [day.strftime("%b %d") for day in date_range]
    training_minutes = [round(training_totals.get(day, 0) / 60, 1) for day in date_range]
    sleep_hours = [round(sleep_totals.get(day, 0) / 3600, 1) for day in date_range]
    fatigue_scores = [fatigue_totals.get(day) for day in date_range]

    return render(
        request,
        "pages/health_progress.html",
        {
            "title": "Progress",
            "headline": "See your last 30 days at a glance.",
            "progress_data": {
                "labels": labels,
                "trainingMinutes": training_minutes,
                "sleepHours": sleep_hours,
                "fatigueScores": fatigue_scores,
            },
        },
        status=200,
    )


@login_required
def health_settings_page(request):
    form = UserSettingsForm(request.user, instance=request.user)
    saved = False

    if request.method == "POST":
        form = UserSettingsForm(request.user, request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            if form.cleaned_data.get("password1"):
                update_session_auth_hash(request, user)
            saved = True
            form = UserSettingsForm(user, instance=user)

    return render(
        request,
        "pages/health_settings.html",
        {
            "title": "Account settings",
            "headline": "Manage your sign-in details and personal info.",
            "form": form,
            "saved": saved,
        },
    )


def _trainer_reports(user: User | None = None):
    today = timezone.localdate()
    return [
        _report_card("Today", today, today, user=user),
        _report_card("Last 7 days", today - timedelta(days=6), today, user=user),
        _report_card("Last 30 days", today - timedelta(days=29), today, user=user),
    ]


def _report_card(title: str, start_date, end_date, user: User | None = None):
    exercise_logs = ExerciseLog.objects.filter(
        completed_at__date__range=(start_date, end_date)
    )
    planned_exercises = DailyExercise.objects.filter(
        scheduled_for__range=(start_date, end_date)
    )
    recoveries = RecoveryLog.objects.filter(recorded_for__range=(start_date, end_date))
    fatigues = FatigueLog.objects.filter(recorded_for__range=(start_date, end_date))

    if user:
        exercise_logs = exercise_logs.filter(user=user)
        planned_exercises = planned_exercises.filter(user=user)
        recoveries = recoveries.filter(user=user)
        fatigues = fatigues.filter(user=user)

    training_seconds = exercise_logs.aggregate(total=Sum("duration_seconds")).get("total") or 0
    planned = planned_exercises.count()
    completed = (
        exercise_logs.values("daily_exercise_id").distinct().count()
    )
    adherence = round((completed / planned) * 100) if planned else 0

    average_sleep = recoveries.aggregate(avg=Avg("sleep_duration")).get("avg")
    fatigue_score = fatigues.aggregate(avg=Avg("total_score")).get("avg")

    range_label = f"{start_date.strftime('%b %d')} – {end_date.strftime('%b %d')}"

    return {
        "title": title,
        "range": range_label,
        "adherence": adherence,
        "training_minutes": round(training_seconds / 60, 1),
        "average_sleep": _hours_from_duration(average_sleep),
        "average_fatigue": round(fatigue_score or 0, 1),
    }


def _trainer_people(user: User | None = None):
    today = timezone.localdate()
    week_start = today - timedelta(days=6)
    accounts = User.objects.order_by("username")
    if user:
        accounts = accounts.filter(id=user.id)

    people = []

    for account in accounts:
        planned = DailyExercise.objects.filter(
            user=account, scheduled_for__range=(week_start, today)
        ).count()
        completed = (
            ExerciseLog.objects.filter(
                user=account, completed_at__date__range=(week_start, today)
            )
            .values("daily_exercise_id")
            .distinct()
            .count()
        )
        adherence = round((completed / planned) * 100) if planned else 0

        next_session = (
            DailyExercise.objects.filter(
                user=account, scheduled_for__gt=today
            ).order_by("scheduled_for", "order")
        ).first()
        todays_plan = DailyExercise.objects.filter(
            user=account, scheduled_for=today
        ).count()
        latest_fatigue = (
            FatigueLog.objects.filter(user=account).order_by("-recorded_for")
        ).first()
        latest_recovery = (
            RecoveryLog.objects.filter(user=account).order_by("-recorded_for")
        ).first()

        people.append(
            {
                "user": account,
                "today_count": todays_plan,
                "next_day": next_session.scheduled_for if next_session else None,
                "fatigue": latest_fatigue.total_score if latest_fatigue else None,
                "sleep_hours": _hours_from_duration(
                    latest_recovery.sleep_duration if latest_recovery else None
                ),
                "adherence": adherence,
                "nutrition": latest_recovery.get_nutrition_display() if latest_recovery else None,
            }
        )

    return people


def _trainer_summary_for_user(user: User):
    summary = _trainer_people(user=user)
    return summary[0] if summary else None


def _upcoming_plan_for_user(user: User):
    today = timezone.localdate()
    end_date = today + timedelta(days=6)
    plan = (
        DailyExercise.objects.filter(user=user, scheduled_for__range=(today, end_date))
        .select_related("exercise")
        .order_by("scheduled_for", "order")
    )

    rows = []
    for daily in plan:
        rows.append(
            {
                "date": daily.scheduled_for,
                "name": daily.exercise.name,
                "sets": daily.sets,
                "reps": daily.repetitions,
                "difficulty": daily.exercise.difficulty_range,
            }
        )

    return rows


def _build_exercise_steps(todays_exercises):
    exercises = list(todays_exercises)
    if not exercises:
        return []

    max_sets = max(item.sets or 1 for item in exercises)
    ordered_sets = []

    for set_number in range(1, max_sets + 1):
        for daily_exercise in exercises:
            sets = daily_exercise.sets or 1
            if set_number <= sets:
                ordered_sets.append({
                    "daily_exercise": daily_exercise,
                    "set_number": set_number,
                })

    return ordered_sets


def _format_sleep_duration(duration):
    total_minutes = int(duration.total_seconds() // 60)
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours}:{minutes:02d}"


def _hours_from_duration(duration):
    if not duration:
        return None
    return round(duration.total_seconds() / 3600, 1)


FAS_OPTIONS = [
    {"value": 1, "label": "Never", "detail": ""},
    {"value": 2, "label": "Sometimes", "detail": "About monthly or less"},
    {"value": 3, "label": "Regularly", "detail": "A few times a month"},
    {"value": 4, "label": "Often", "detail": "About weekly"},
    {"value": 5, "label": "Always", "detail": "About every day"},
]

FAS_QUESTIONS = [
    {"id": 1, "text": "I am bothered by fatigue", "reversed": False},
    {"id": 2, "text": "I get tired very quickly", "reversed": False},
    {"id": 3, "text": "I don't do much during the day", "reversed": False},
    {"id": 4, "text": "I have enough energy for everyday life", "reversed": True},
    {"id": 5, "text": "Physically I feel exhausted", "reversed": False},
    {"id": 6, "text": "I have problems to start things", "reversed": False},
    {"id": 7, "text": "I have problems to think clearly", "reversed": False},
    {"id": 8, "text": "I feel no desire to do anything", "reversed": False},
    {"id": 9, "text": "Mentally I feel exhausted", "reversed": False},
    {"id": 10, "text": "When doing something, I can concentrate well", "reversed": True},
]


def _select_fas_questions(session, responses=None):
    selected_ids = session.get("fas_question_ids")

    if responses:
        selected = [
            {
                "id": response["question_id"],
                "text": response.get("question")
                or next(
                    (q["text"] for q in FAS_QUESTIONS if q["id"] == response["question_id"]),
                    "",
                ),
                "reversed": response.get("reversed", False),
            }
            for response in responses
        ]
        session["fas_question_ids"] = [question["id"] for question in selected]
    elif selected_ids:
        selected = [
            question
            for question in FAS_QUESTIONS
            if question["id"] in selected_ids
        ]
    else:
        selected = random.sample(FAS_QUESTIONS, 5)
        session["fas_question_ids"] = [question["id"] for question in selected]

    return [
        {**question, "field_name": f"question_{question['id']}"}
        for question in selected
    ]


def _fas_initial_from_responses(responses):
    if not responses:
        return {}

    return {
        f"question_{response['question_id']}": response.get("value", 1)
        for response in responses
    }


def _calculate_fas_score(responses, questions):
    total = 0
    for question in questions:
        value = responses.get(question["field_name"], 0)
        adjusted_value = 6 - value if question["reversed"] else value
        total += adjusted_value
    return total


@login_required
def exercise_session_page(request):
    ensure_training_tables_ready()

    todays_exercises = list(
        DailyExercise.objects.filter(
            user=request.user, scheduled_for=timezone.localdate()
        ).select_related("exercise")
    )

    exercise_steps = _build_exercise_steps(todays_exercises)
    total_steps = len(exercise_steps) + 2  # sleep/nutrition + fatigue

    completed_logs = ExerciseLog.objects.filter(
        user=request.user, daily_exercise__in=[step["daily_exercise"] for step in exercise_steps]
    ).count()
    completed_logs = min(completed_logs, len(exercise_steps))

    post_exercise_stage = int(request.session.get("post_exercise_stage", 0) or 0)
    if completed_logs < len(exercise_steps):
        post_exercise_stage = 0

    if post_exercise_stage == 0:
        request.session.pop("fas_question_ids", None)
        request.session.pop("fas_responses", None)
        request.session.pop("fas_total_score", None)

    recorded_for = timezone.localdate()
    recovery_log = RecoveryLog.objects.filter(user=request.user, recorded_for=recorded_for).first()
    fatigue_log = FatigueLog.objects.filter(user=request.user, recorded_for=recorded_for).first()

    session_finished = (
        exercise_steps
        and completed_logs >= len(exercise_steps)
        and recovery_log
        and fatigue_log
    )

    completed_post_exercise_stage = 0
    if recovery_log:
        completed_post_exercise_stage = 1
        if fatigue_log:
            completed_post_exercise_stage = 2

    if post_exercise_stage > completed_post_exercise_stage:
        post_exercise_stage = completed_post_exercise_stage
        request.session["post_exercise_stage"] = post_exercise_stage

    editing_checkins = session_finished and (
        request.GET.get("edit_checkins") == "1"
        or request.session.get("editing_checkins")
    )
    if editing_checkins:
        request.session["editing_checkins"] = True
        if post_exercise_stage >= 2 or post_exercise_stage == 0:
            post_exercise_stage = 0
            request.session["current_step_started_at"] = timezone.now().timestamp()
            request.session.pop("fas_question_ids", None)
            request.session.pop("fas_responses", None)
            request.session.pop("fas_total_score", None)
        request.session["post_exercise_stage"] = post_exercise_stage
    else:
        request.session.pop("editing_checkins", None)

    if (
        recovery_log
        and completed_logs >= len(exercise_steps)
        and post_exercise_stage == 0
        and not editing_checkins
    ):
        post_exercise_stage = 1
        request.session["post_exercise_stage"] = post_exercise_stage

    completed_steps = completed_logs + min(post_exercise_stage, 2)
    current_step_number = min(completed_steps + 1, total_steps)
    progress_percent = (completed_steps / total_steps) * 100 if total_steps else 0

    current_timestamp = timezone.now()
    session_started_at = request.session.get("current_step_started_at")
    if session_started_at is None:
        request.session["current_step_started_at"] = current_timestamp.timestamp()
        session_started_at = request.session["current_step_started_at"]
    else:
        session_started_at = float(session_started_at)

    recovery_form = None
    fas_form = None
    fas_questions = []
    fas_initial = _fas_initial_from_responses(fatigue_log.responses if fatigue_log else None)

    if request.method == "POST":
        started_at = datetime.fromtimestamp(session_started_at, tz=timezone.get_current_timezone())
        duration_seconds = max(int(current_timestamp.timestamp() - session_started_at), 1)

        if completed_logs < len(exercise_steps):
            current_step = exercise_steps[completed_logs]
            ExerciseLog.objects.update_or_create(
                user=request.user,
                daily_exercise=current_step["daily_exercise"],
                set_number=current_step["set_number"],
                defaults={
                    "duration_seconds": duration_seconds,
                    "started_at": started_at,
                    "completed_at": current_timestamp,
                },
            )
            request.session["post_exercise_stage"] = 0
            request.session["current_step_started_at"] = timezone.now().timestamp()
            return redirect("exercise_session")
        elif post_exercise_stage == 0:
            recovery_form = RecoveryLogForm(request.POST)
            if recovery_form.is_valid():
                RecoveryLog.objects.update_or_create(
                    user=request.user,
                    recorded_for=recorded_for,
                    defaults=recovery_form.cleaned_data,
                )
                post_exercise_stage = 1
                request.session["post_exercise_stage"] = post_exercise_stage
                request.session["current_step_started_at"] = timezone.now().timestamp()
                return redirect("exercise_session")
        elif post_exercise_stage == 1:
            fas_questions = _select_fas_questions(
                request.session, responses=fatigue_log.responses if fatigue_log else None
            )
            fas_form = FatigueAssessmentForm(request.POST, questions=fas_questions)
            if fas_form.is_valid():
                responses = {
                    field: fas_form.cleaned_data[field]
                    for field in fas_form.fields
                }
                total_score = _calculate_fas_score(responses, fas_questions)
                structured_responses = [
                    {
                        "question_id": question["id"],
                        "question": question["text"],
                        "reversed": question["reversed"],
                        "value": responses.get(question["field_name"], 0),
                    }
                    for question in fas_questions
                ]
                FatigueLog.objects.update_or_create(
                    user=request.user,
                    recorded_for=recorded_for,
                    defaults={
                        "responses": structured_responses,
                        "total_score": total_score,
                    },
                )
                request.session["fas_responses"] = responses
                request.session["fas_total_score"] = total_score
                post_exercise_stage = min(post_exercise_stage + 1, 2)
                request.session["post_exercise_stage"] = post_exercise_stage
                request.session.pop("editing_checkins", None)
                request.session["current_step_started_at"] = timezone.now().timestamp()
                return redirect("exercise_session")
        else:
            post_exercise_stage = min(post_exercise_stage + 1, 2)
            request.session["post_exercise_stage"] = post_exercise_stage
            request.session.pop("editing_checkins", None)
            request.session["current_step_started_at"] = timezone.now().timestamp()
            return redirect("exercise_session")

    if recovery_form is None and post_exercise_stage == 0:
        initial = {}
        if recovery_log:
            initial = {
                "sleep_duration": _format_sleep_duration(recovery_log.sleep_duration),
                "sleep_quality": recovery_log.sleep_quality,
                "nutrition": recovery_log.nutrition,
                "comment": recovery_log.comment,
            }
        recovery_form = RecoveryLogForm(initial=initial)

    if post_exercise_stage == 1:
        if not fas_questions:
            fas_questions = _select_fas_questions(
                request.session, responses=fatigue_log.responses if fatigue_log else None
            )
        if fas_form is None:
            fas_form = FatigueAssessmentForm(questions=fas_questions, initial=fas_initial)
        if fas_form and fas_questions:
            for question in fas_questions:
                question["form_field"] = fas_form[question["field_name"]]

    context = {
        "title": "Exercise session",
        "headline": "Work through today\'s plan one set at a time.",
        "steps": exercise_steps,
        "current_step": exercise_steps[completed_logs] if completed_logs < len(exercise_steps) else None,
        "current_set_number": exercise_steps[completed_logs]["set_number"] if completed_logs < len(exercise_steps) else None,
        "total_steps": total_steps,
        "current_step_number": current_step_number,
        "progress_percent": progress_percent,
        "post_exercise_stage": post_exercise_stage,
        "recovery_form": recovery_form,
        "fas_form": fas_form,
        "fas_questions": fas_questions,
        "fas_options": FAS_OPTIONS,
    }

    return render(request, "pages/exercise_session.html", context)


