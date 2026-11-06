from django.core.management import call_command
from django.core.management.base import BaseCommand
from tracker.models import Developer, Technology, Status, Project


class Command(BaseCommand):
    help = "Подготовить начальные данные без перезаписи существующих записей"

    def handle(self, *args, **options):
        if any(
            model.objects.exists() for model in (Developer, Technology, Status, Project)
        ):
            self.stdout.write("Данные уже существуют; повторный импорт не требуется.")
        else:
            call_command("import_json", stdout=self.stdout)
