from django.db import migrations

BASIC_GROUP_NAME = "basic user"
TRAINER_GROUP_NAME = "trainer user"


def create_default_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name=BASIC_GROUP_NAME)
    Group.objects.get_or_create(name=TRAINER_GROUP_NAME)


def remove_default_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=[BASIC_GROUP_NAME, TRAINER_GROUP_NAME]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
