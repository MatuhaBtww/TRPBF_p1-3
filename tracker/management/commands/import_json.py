from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from service import decode, encode
from storage import read_json
from tracker.models import Developer, Technology, Status, Project

class Command(BaseCommand):
    help = 'Перенос JSON в пустые предметные таблицы без изменения исходного файла'

    def add_arguments(self, parser):
        parser.add_argument('--source', type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        if any(m.objects.exists() for m in (Developer,Technology,Status,Project)):
            raise CommandError('Предметные таблицы уже заполнены. Импорт отменен без перезаписи.')
        folder = settings.BASE_DIR/'data'
        source = options['source'] or folder/('runtime.json' if (folder/'runtime.json').exists() else 'seed.json')
        try:
            data = encode(decode(read_json(source)))
        except (OSError,ValueError,KeyError,TypeError) as error:
            raise CommandError(str(error)) from error
        for kind,model in [('developers',Developer),('technologies',Technology),('statuses',Status)]:
            for row in data[kind]:
                obj=model(id=row['id'],name=row['name'])
                obj.full_clean()
                obj.save()
        for p in data['projects']:
            obj=Project(id=p['id'],name=p['name'],developer_id=p['developer_id'],status_id=p['status_id'],deadline=p['deadline'])
            obj.save()
            obj.technologies.set(p['technology_ids'])
        self.stdout.write(str({kind:len(rows) for kind,rows in data.items()}))
