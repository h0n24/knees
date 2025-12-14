from __future__ import annotations

import json
import random
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable, List

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection, transaction
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone

from apps.backend.training.models import (
    DailyExercise,
    Exercise,
    ExerciseLog,
    FatigueLog,
    RecoveryLog,
)


EXERCISE_COUNT_PER_DAY = 5
MAX_DIFFICULTY_PER_DAY = 10


def _library_path() -> Path:
    return Path(settings.BASE_DIR) / "exercises.json"


def ensure_training_tables_ready() -> None:
    """Apply migrations if the training tables have not been created yet.

    When the project is first run it's easy to forget the ``migrate`` step,
    which leads to ``OperationalError: no such table: training_exercise`` when
    we try to seed the exercise library. To keep the registration flow stable
    in development, we opportunistically run migrations if the training tables
    are missing.
    """

    table_name = Exercise._meta.db_table
    try:
        if table_name in connection.introspection.table_names():
            return
    except (OperationalError, ProgrammingError):
        # SQLite may raise if the database file hasn't been created yet.
        pass

    call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)


def ensure_library_loaded() -> List[Exercise]:
    """Load exercises from the bundled JSON file into the database if missing."""

    ensure_training_tables_ready()

    path = _library_path()
    with path.open() as handle:
        data = json.load(handle)

    exercises: list[Exercise] = []
    for raw in data.get("exercises", []):
        exercise, _ = Exercise.objects.update_or_create(
            external_id=raw["id"],
            defaults={
                "name": raw["name"],
                "difficulty_min": raw["difficulty"]["min"],
                "difficulty_max": raw["difficulty"]["max"],
                "categories": raw.get("categories", []),
                "prescription": raw.get("prescription", {}),
                "notes": raw.get("notes", ""),
            },
        )
        exercises.append(exercise)
    return exercises


def _pick_daily_set(exercises: Iterable[Exercise]) -> list[Exercise]:
    pool = list(exercises)
    if len(pool) < EXERCISE_COUNT_PER_DAY:
        return pool

    for _ in range(50):
        selection = random.sample(pool, k=EXERCISE_COUNT_PER_DAY)
        difficulty = sum(item.difficulty_max for item in selection)
        if difficulty <= MAX_DIFFICULTY_PER_DAY:
            return selection

    sorted_pool = sorted(pool, key=lambda e: e.difficulty_max)
    chosen: list[Exercise] = []
    total = 0
    for exercise in sorted_pool:
        if len(chosen) >= EXERCISE_COUNT_PER_DAY:
            break
        if total + exercise.difficulty_max <= MAX_DIFFICULTY_PER_DAY:
            chosen.append(exercise)
            total += exercise.difficulty_max

    for exercise in sorted_pool:
        if len(chosen) >= EXERCISE_COUNT_PER_DAY:
            break
        if exercise not in chosen:
            chosen.append(exercise)
    return chosen[:EXERCISE_COUNT_PER_DAY]


def _min_prescription_value(exercise: Exercise, field: str) -> int | None:
    prescription = exercise.prescription or {}
    values = prescription.get(field)
    if isinstance(values, dict):
        return values.get("min")
    return None


@transaction.atomic
def create_weekly_plan_for_user(user: User) -> list[DailyExercise]:
    exercises = ensure_library_loaded()
    created: list[DailyExercise] = []
    today = date.today()

    for offset in range(7):
        scheduled_day = today + timedelta(days=offset)
        if DailyExercise.objects.filter(user=user, scheduled_for=scheduled_day).exists():
            continue
        daily_selection = _pick_daily_set(exercises)
        new_entries = [
            DailyExercise(
                user=user,
                exercise=exercise,
                scheduled_for=scheduled_day,
                order=index,
                sets=_min_prescription_value(exercise, "sets"),
                repetitions=_min_prescription_value(exercise, "reps"),
            )
            for index, exercise in enumerate(daily_selection)
        ]
        created.extend(DailyExercise.objects.bulk_create(new_entries))

    return created


def _sample_responses() -> list[dict]:
    questions = [
        "How do your knees feel today?",
        "Any soreness while walking?",
        "How was recovery after your last session?",
        "Are you ready for your next workout?",
    ]
    responses: list[dict] = []
    for question in questions:
        answer = random.randint(0, 4)
        responses.append({"question": question, "answer": answer})
    return responses


def generate_recovery_logs_for_all_users(retrospective_days: int = 30) -> int:
    start_day = timezone.localdate() - timedelta(days=retrospective_days - 1)
    created = 0
    for user in User.objects.all():
        for offset in range(retrospective_days):
            recorded_for = start_day + timedelta(days=offset)
            _, was_created = RecoveryLog.objects.get_or_create(
                user=user,
                recorded_for=recorded_for,
                defaults={
                    "sleep_duration": timedelta(
                        hours=random.randint(6, 9),
                        minutes=random.choice([0, 15, 30, 45]),
                    ),
                    "sleep_quality": random.randint(60, 100),
                    "nutrition": random.choice(
                        [choice[0] for choice in RecoveryLog.NutritionQuality.choices]
                    ),
                    "comment": "Automated demo recovery log.",
                },
            )
            created += 1 if was_created else 0
    return created


def generate_fatigue_logs_for_all_users(retrospective_days: int = 30) -> int:
    start_day = timezone.localdate() - timedelta(days=retrospective_days - 1)
    created = 0
    for user in User.objects.all():
        for offset in range(retrospective_days):
            recorded_for = start_day + timedelta(days=offset)
            responses = _sample_responses()
            total_score = sum(item["answer"] for item in responses)
            _, was_created = FatigueLog.objects.get_or_create(
                user=user,
                recorded_for=recorded_for,
                defaults={"responses": responses, "total_score": total_score},
            )
            created += 1 if was_created else 0
    return created


def _exercise_times_for_day(target_day: date, sets: int) -> list[tuple[datetime, datetime]]:
    start_of_day = datetime.combine(
        target_day, time(hour=8), tzinfo=timezone.get_current_timezone()
    )
    times: list[tuple[datetime, datetime]] = []
    for index in range(sets):
        started = start_of_day + timedelta(minutes=30 * index)
        completed = started + timedelta(minutes=random.randint(5, 12))
        times.append((started, completed))
    return times


def generate_exercise_logs_for_all_users(days_ago: int = 30) -> dict[str, int]:
    ensure_library_loaded()
    created_daily = 0
    created_logs = 0
    target_day = timezone.localdate() - timedelta(days=days_ago)
    for user in User.objects.all():
        daily_selection = _pick_daily_set(Exercise.objects.all())
        for order, exercise in enumerate(daily_selection):
            daily, daily_created = DailyExercise.objects.get_or_create(
                user=user,
                scheduled_for=target_day,
                order=order,
                defaults={
                    "exercise": exercise,
                    "sets": _min_prescription_value(exercise, "sets"),
                    "repetitions": _min_prescription_value(exercise, "reps"),
                },
            )
            created_daily += 1 if daily_created else 0
            set_count = daily.sets or random.randint(2, 3)
            for set_number, (started, completed) in enumerate(
                _exercise_times_for_day(target_day, set_count), start=1
            ):
                _, log_created = ExerciseLog.objects.get_or_create(
                    user=user,
                    daily_exercise=daily,
                    set_number=set_number,
                    defaults={
                        "duration_seconds": int((completed - started).total_seconds()),
                        "started_at": started,
                        "completed_at": completed,
                    },
                )
                created_logs += 1 if log_created else 0
    return {"daily": created_daily, "logs": created_logs}


def generate_all_account_test_data() -> dict[str, int]:
    recovery = generate_recovery_logs_for_all_users()
    fatigue = generate_fatigue_logs_for_all_users()
    exercise = generate_exercise_logs_for_all_users()
    return {
        "recovery": recovery,
        "fatigue": fatigue,
        "daily": exercise["daily"],
        "exercise_logs": exercise["logs"],
    }
