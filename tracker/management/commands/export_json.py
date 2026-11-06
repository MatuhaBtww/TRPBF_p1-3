from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from service import decode, encode
from storage import write_json
from tracker.models import Developer, Technology, Status, Project


class Command(BaseCommand):
    help = "Экспортировать данные ORM в совместимый с ПР3 JSON без перезаписи файлов"

    def add_arguments(self, parser):
        parser.add_argument("--output", required=True, type=Path)

    def handle(self, *args, **options):
        path = options["output"]
        if path.exists():
            raise CommandError("Файл уже существует. Выберите новое имя для экспорта.")
        data = {
            name: list(model.objects.order_by("pk").values("id", "name"))
            for name, model in [
                ("developers", Developer),
                ("technologies", Technology),
                ("statuses", Status),
            ]
        }
        data["projects"] = [
            {
                "id": p.pk,
                "name": p.name,
                "deadline": p.deadline.isoformat(),
                "developer_id": p.developer_id,
                "status_id": p.status_id,
                "technology_ids": sorted(t.pk for t in p.technologies.all()),
            }
            for p in Project.objects.prefetch_related("technologies").order_by("pk")
        ]
        write_json(path, encode(decode(data)))
        self.stdout.write(f"Экспорт сохранен: {path}")
