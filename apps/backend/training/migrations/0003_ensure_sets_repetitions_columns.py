from django.db import migrations, models


def ensure_sets_and_repetitions(apps, schema_editor):
    DailyExercise = apps.get_model("training", "DailyExercise")
    table_name = DailyExercise._meta.db_table

    with schema_editor.connection.cursor() as cursor:
        existing_columns = {
            column.name for column in schema_editor.connection.introspection.get_table_description(cursor, table_name)
        }

    def add_field_if_missing(field_name: str):
        if field_name in existing_columns:
            return
        field = models.PositiveSmallIntegerField(null=True, blank=True)
        field.set_attributes_from_name(field_name)
        schema_editor.add_field(DailyExercise, field)

    add_field_if_missing("sets")
    add_field_if_missing("repetitions")


class Migration(migrations.Migration):

    dependencies = [
        ("training", "0002_dailyexercise_repetitions_dailyexercise_sets"),
    ]

    operations = [
        migrations.RunPython(ensure_sets_and_repetitions, migrations.RunPython.noop),
    ]
