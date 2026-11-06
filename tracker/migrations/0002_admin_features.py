from django.db import migrations, models
from django.db.models.functions import Lower
import tracker.models


def populate(apps, schema_editor):
    Status = apps.get_model("tracker", "Status")
    for pk, code in [(1, "planned"), (2, "active"), (3, "completed")]:
        Status.objects.filter(pk=pk).update(code=code)
    Project = apps.get_model("tracker", "Project")
    for obj in Project.objects.all():
        obj.slug = f"project-{obj.pk}"
        obj.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("tracker", "0001_initial")]
    operations = [
        migrations.AddField(
            "status",
            "code",
            models.CharField(max_length=12, null=True, verbose_name="Код"),
        ),
        migrations.AddField(
            "project",
            "slug",
            models.SlugField(max_length=80, null=True, verbose_name="Адрес"),
        ),
        migrations.RunPython(populate, migrations.RunPython.noop),
        migrations.AlterField(
            "status",
            "code",
            models.CharField(
                max_length=12,
                unique=True,
                choices=[
                    ("planned", "Запланирован"),
                    ("active", "В работе"),
                    ("completed", "Завершен"),
                ],
                verbose_name="Код",
            ),
        ),
        migrations.AlterField(
            "project",
            "slug",
            models.SlugField(
                max_length=80,
                unique=True,
                default=tracker.models.new_slug,
                verbose_name="Адрес",
            ),
        ),
        migrations.AddField(
            "project",
            "is_completed",
            models.GeneratedField(
                expression=models.Case(
                    models.When(status_id=3, then=models.Value(True)),
                    default=models.Value(False),
                ),
                output_field=models.BooleanField(),
                db_persist=True,
            ),
        ),
        migrations.AddConstraint(
            "developer",
            models.UniqueConstraint(Lower("name"), name="unique_developer_name"),
        ),
        migrations.AddConstraint(
            "technology",
            models.UniqueConstraint(Lower("name"), name="unique_technology_name"),
        ),
    ]
