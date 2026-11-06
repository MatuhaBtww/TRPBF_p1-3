from datetime import date
from io import StringIO
import json

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.test import Client

from db.import_json import import_data
from db.database import connect
from db.check_queries import verify
from tracker.forms import ProjectForm
from tracker.models import Project, Developer, Technology


@pytest.fixture
def seeded(db):
    call_command("import_json", stdout=StringIO())
    return Project.objects.get(pk=2)


def test_sql_import_queries_and_constraints(tmp_path):
    from django.conf import settings

    db = tmp_path / "legacy.sqlite3"
    counts = import_data(settings.BASE_DIR / "data/seed.json", db)
    assert counts == {"developers": 2, "technologies": 2, "statuses": 3, "projects": 2}
    assert len(verify(db)) == 12
    with connect(db) as con:
        assert (
            con.execute("SELECT COUNT(*) FROM project_technologies").fetchone()[0] == 3
        )
        assert not con.execute("PRAGMA foreign_key_check").fetchall()
    with pytest.raises(ValueError):
        import_data(settings.BASE_DIR / "data/seed.json", db)
    with connect(db) as con:
        assert con.execute("SELECT COUNT(*) FROM projects").fetchone()[0] == 2


@pytest.mark.django_db
def test_replace_only_technology_in_form(seeded):
    form = ProjectForm(
        data={
            "name": seeded.name,
            "developer": 2,
            "technologies": [2],
            "deadline": "2026-09-20",
            "status": 1,
        },
        instance=seeded,
    )
    assert form.is_valid(), form.errors
    form.save()
    assert list(seeded.technologies.values_list("pk", flat=True)) == [2]


@pytest.mark.django_db
@pytest.mark.parametrize("model", [Developer, Technology])
def test_reference_unicode_duplicates_rejected(model):
    model.objects.create(name="Технология")
    with pytest.raises(ValidationError):
        model.objects.create(name="  ТЕХНОЛОГИЯ  ")


@pytest.mark.django_db
def test_new_project_cannot_skip_planned_status(seeded):
    form = ProjectForm(
        data={
            "name": "Новый",
            "developer": 1,
            "technologies": [1],
            "deadline": "2026-12-01",
            "status": 3,
        }
    )
    assert not form.is_valid()
    assert "status" in form.errors


@pytest.mark.django_db
def test_deleting_technologies_in_bulk_preserves_projects(seeded):
    with pytest.raises(ProtectedError), transaction.atomic():
        Technology.objects.all().delete()
    assert Technology.objects.count() == 2
    assert all(p.technologies.exists() for p in Project.objects.all())


@pytest.mark.django_db
def test_admin_handles_protected_technology_delete(admin_client, seeded):
    response = admin_client.get("/admin/tracker/technology/1/delete/")
    assert response.status_code == 200
    assert "нельзя удалить все" in response.content.decode()
    response = admin_client.post("/admin/tracker/technology/1/delete/", {"post": "yes"})
    assert response.status_code == 200
    assert Technology.objects.filter(pk=1).exists()


@pytest.mark.django_db
def test_admin_bulk_status_actions_respect_rules(admin_client, seeded):
    response = admin_client.post(
        "/admin/tracker/project/",
        {"action": "start_projects", "_selected_action": [1, 2], "index": 0},
        follow=True,
    )
    assert response.status_code == 200
    assert "Изменено: 1." in response.content.decode()
    assert list(Project.objects.order_by("pk").values_list("status_id", flat=True)) == [
        2,
        2,
    ]
    response = admin_client.post(
        "/admin/tracker/project/",
        {"action": "complete_projects", "_selected_action": [1, 2], "index": 0},
        follow=True,
    )
    assert response.status_code == 200
    assert Project.objects.completed().count() == 2
    admin_client.post(
        "/admin/tracker/project/",
        {"action": "plan_projects", "_selected_action": [1, 2], "index": 0},
        follow=True,
    )
    assert Project.objects.completed().count() == 2


@pytest.mark.django_db
def test_admin_deadline_editable_in_list(admin_client, seeded):
    response = admin_client.get("/admin/tracker/project/")
    formset = response.context["cl"].formset
    data = {
        "_save": "Сохранить",
        "form-TOTAL_FORMS": len(formset.forms),
        "form-INITIAL_FORMS": len(formset.forms),
        "form-MIN_NUM_FORMS": 0,
        "form-MAX_NUM_FORMS": 1000,
    }
    for number, form in enumerate(formset.forms):
        data[f"form-{number}-id"] = form.instance.pk
        data[f"form-{number}-deadline"] = "2027-01-05"
    response = admin_client.post("/admin/tracker/project/", data, follow=True)
    assert response.status_code == 200
    assert all(p.deadline == date(2027, 1, 5) for p in Project.objects.all())


@pytest.mark.django_db
def test_bootstrap_admin_persistent_idempotent_and_readonly_group(
    client, tmp_path, seeded
):
    path = tmp_path / "access.txt"
    call_command(
        "bootstrap_admin", with_viewer=True, credentials=path, stdout=StringIO()
    )
    user = get_user_model().objects.get(username="matvey")
    old_hash = user.password
    assert user.is_superuser and user.is_active and user.is_staff
    assert "Пароль:" in path.read_text(encoding="utf-8")
    call_command(
        "bootstrap_admin", with_viewer=True, credentials=path, stdout=StringIO()
    )
    user.refresh_from_db()
    assert user.password == old_hash
    viewer = get_user_model().objects.get(username="observer")
    assert viewer.groups.filter(name="Наблюдатели").exists()
    client.force_login(viewer)
    assert client.get("/admin/tracker/project/").status_code == 200
    assert client.get("/projects/new/").status_code == 403
    assert client.get("/projects/1/edit/").status_code == 403
    assert client.post("/projects/1/delete/").status_code == 403


@pytest.mark.django_db
def test_staff_without_model_permission_denied(client, seeded):
    user = get_user_model().objects.create_user(username="limited", is_staff=True)
    client.force_login(user)
    assert client.post("/projects/new/", {}).status_code == 403
    assert client.post("/developers/new/", {}).status_code == 403


@pytest.mark.django_db
def test_login_logout_and_csrf(seeded):
    user = get_user_model().objects.create_user(
        username="tester", password="Test-login-2026!", is_staff=True, is_superuser=True
    )
    client = Client(enforce_csrf_checks=True)
    assert client.get("/accounts/login/").status_code == 200
    token = client.cookies["csrftoken"].value
    response = client.post(
        "/accounts/login/",
        {
            "username": user.username,
            "password": "Test-login-2026!",
            "csrfmiddlewaretoken": token,
        },
    )
    assert response.status_code == 302
    assert client.post("/projects/1/delete/").status_code == 403
    assert client.get("/accounts/logout/").status_code == 405
    response = client.post(
        "/accounts/logout/", {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_reference_crud_and_protected_delete(admin_client, seeded):
    response = admin_client.post("/developers/new/", {"name": "Свободный разработчик"})
    assert response.status_code == 302
    p = Developer.objects.get(name="Свободный разработчик")
    assert (
        admin_client.post(
            f"/developers/{p.pk}/edit/", {"name": "Новое имя"}
        ).status_code
        == 302
    )
    assert admin_client.post(f"/developers/{p.pk}/delete/").status_code == 302
    assert not Developer.objects.filter(pk=p.pk).exists()
    response = admin_client.post("/developers/2/delete/")
    assert response.status_code == 200
    assert "Запись используется проектами" in response.content.decode()
    assert Developer.objects.filter(pk=2).exists()
    assert admin_client.post("/technologies/1/delete/").status_code == 200


@pytest.mark.django_db
def test_project_delete_requires_confirmation(admin_client, seeded):
    assert admin_client.get("/projects/2/delete/").status_code == 200
    assert Project.objects.filter(pk=2).exists()
    assert admin_client.post("/projects/2/delete/").status_code == 302
    assert not Project.objects.filter(pk=2).exists()


@pytest.mark.django_db
def test_table_and_csv_share_filters_and_F_labels(client, seeded):
    response = client.get("/projects/?view=table&status=2")
    assert response.status_code == 200
    rows = list(response.context["projects"])
    assert len(rows) == 1 and rows[0]["developer_name"] == "Анна Смирнова"
    response = client.get("/projects/export/?status=2")
    assert response.status_code == 200
    text = response.content.decode("utf-8-sig")
    assert "Анна Смирнова" in text and "Сервис отчетов" not in text


@pytest.mark.django_db
def test_filters_by_date_developer_and_technology(client, seeded):
    response = client.get(
        "/projects/?date=2026-12-20&developer=1&technology=2&sort=developer"
    )
    assert response.status_code == 200
    assert [p.pk for p in response.context["projects"]] == [1]
    response = client.get("/projects/?date=bad&developer=999")
    assert response.status_code == 400
    assert response.context["form"].errors


@pytest.mark.django_db
def test_empty_state_and_zero_groups(client):
    for url in [
        "/",
        "/projects/",
        "/statistics/",
        "/developers/",
        "/technologies/",
        "/available/",
    ]:
        assert client.get(url).status_code == 200
    Developer.objects.create(name="Без проектов")
    response = client.get("/statistics/")
    assert response.context["stats"]["Всего проектов"] == 0
    assert list(response.context["developers"])[0].total == 0


@pytest.mark.django_db
def test_json_export_roundtrip_and_no_overwrite(tmp_path, seeded):
    from service import decode, encode

    path = tmp_path / "export.json"
    call_command("export_json", output=path, stdout=StringIO())
    data = json.loads(path.read_text(encoding="utf-8"))
    assert encode(decode(data)) == data
    assert len(data["projects"]) == 2
    with pytest.raises(CommandError):
        call_command("export_json", output=path)


@pytest.mark.django_db(transaction=True)
def test_migration_1_to_3_preserves_data_slug_and_status_codes():
    from django.db import connection
    from django.db.migrations.executor import MigrationExecutor

    executor = MigrationExecutor(connection)
    latest = executor.loader.graph.leaf_nodes("tracker")
    try:
        executor.migrate([("tracker", "0001_initial")])
        apps = executor.loader.project_state([("tracker", "0001_initial")]).apps
        OldStatus = apps.get_model("tracker", "Status")
        OldDeveloper = apps.get_model("tracker", "Developer")
        OldTechnology = apps.get_model("tracker", "Technology")
        OldProject = apps.get_model("tracker", "Project")
        OldStatus.objects.bulk_create(
            [
                OldStatus(id=i, name=name)
                for i, name in [(1, "Запланирован"), (2, "В работе"), (3, "Завершен")]
            ]
        )
        OldDeveloper.objects.create(id=17, name="До миграции")
        OldTechnology.objects.create(id=19, name="Python")
        p = OldProject.objects.create(
            id=23,
            name="Старый проект",
            developer_id=17,
            status_id=2,
            deadline="2026-12-20",
        )
        p.technologies.add(19)
        executor = MigrationExecutor(connection)
        executor.migrate(latest)
        result = Project.objects.get(pk=23)
        assert result.slug == "project-23"
        assert result.status.code == "active"
        assert result.developer_id == 17
        assert list(result.technologies.values_list("pk", flat=True)) == [19]
        assert result.deadline == date(2026, 12, 20)
    finally:
        MigrationExecutor(connection).migrate(latest)
