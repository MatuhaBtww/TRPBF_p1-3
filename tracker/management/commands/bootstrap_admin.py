from pathlib import Path
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Создать локального администратора и роль просмотра; существующие пароли не менять"

    def add_arguments(self, parser):
        parser.add_argument("--username", default="matvey")
        parser.add_argument("--with-viewer", action="store_true")
        parser.add_argument("--credentials", type=Path)

    @transaction.atomic
    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name="Наблюдатели")
        group.permissions.set(
            Permission.objects.filter(
                content_type__app_label="tracker", codename__startswith="view_"
            )
        )
        user_model = get_user_model()
        credentials = []
        if not user_model.objects.filter(username=options["username"]).exists():
            password = secrets.token_urlsafe(20)
            user_model.objects.create_superuser(
                username=options["username"],
                password=password,
                first_name="Матвей",
                last_name="Семин",
            )
            credentials.append(
                f"Администратор\nЛогин: {options['username']}\nПароль: {password}\n"
            )
        if (
            options["with_viewer"]
            and not user_model.objects.filter(username="observer").exists()
        ):
            password = secrets.token_urlsafe(20)
            viewer = user_model.objects.create_user(
                username="observer", password=password, is_staff=True
            )
            viewer.groups.add(group)
            credentials.append(
                f"Просмотр без изменения данных\nЛогин: observer\nПароль: {password}\n"
            )
        if credentials:
            path = (
                options["credentials"]
                or settings.BASE_DIR / ".private/admin-access.txt"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as stream:
                stream.write(
                    "Вход: http://127.0.0.1:8000/accounts/login/\nПанель: http://127.0.0.1:8000/admin/\n\n"
                    + "\n".join(credentials)
                    + "\n"
                )
            self.stdout.write(f"Учетные записи созданы. Данные входа: {path}")
        else:
            self.stdout.write("Учетные записи уже существуют. Пароли не изменены.")
