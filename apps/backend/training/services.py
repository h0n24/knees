from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, List

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.db import connection, transaction
from django.db.utils import OperationalError, ProgrammingError

from apps.backend.training.models import DailyExercise, Exercise


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
            )
            for index, exercise in enumerate(daily_selection)
        ]
        created.extend(DailyExercise.objects.bulk_create(new_entries))

    return created
