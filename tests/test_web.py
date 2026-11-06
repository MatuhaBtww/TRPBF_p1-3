from datetime import date
from io import StringIO
import json
import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management import call_command, CommandError
from django.db import connection
from django.db.models.deletion import ProtectedError
from django.test.utils import CaptureQueriesContext
from tracker.models import Developer, Technology, Status, Project
from tracker.orm_examples import examples


@pytest.fixture
def state(db):
    call_command("import_json", stdout=StringIO())
    return Project.objects.get(pk=1)


@pytest.mark.django_db
def test_import_preserves_all_data_and_links(state):
    source = json.loads(
        (settings.BASE_DIR / "data/seed.json").read_text(encoding="utf-8")
    )
    for name, model in [
        ("developers", Developer),
        ("technologies", Technology),
        ("statuses", Status),
    ]:
        assert list(model.objects.order_by("pk").values("id", "name")) == source[name]
    for p in source["projects"]:
        obj = Project.objects.get(pk=p["id"])
        assert (
            obj.name,
            obj.developer_id,
            obj.status_id,
            obj.deadline.isoformat(),
        ) == (p["name"], p["developer_id"], p["status_id"], p["deadline"])
        assert sorted(obj.technologies.values_list("pk", flat=True)) == sorted(
            p["technology_ids"]
        )


@pytest.mark.django_db
def test_import_does_not_overwrite(state):
    state.name = "Измененное название"
    state.save()
    with pytest.raises(CommandError):
        call_command("import_json")
    state.refresh_from_db()
    assert state.name == "Измененное название"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    [
        "/",
        "/about/",
        "/projects/",
        "/projects/1/",
        "/developers/",
        "/developers/1/",
        "/technologies/",
        "/statistics/",
        "/available/",
    ],
)
def test_pages(client, state, path):
    assert client.get(path).status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "path",
    ["/projects/999/", "/developers/999/", "/projects/by-slug/missing/", "/not-found/"],
)
def test_404(client, state, settings, path):
    settings.DEBUG = False
    response = client.get(path)
    assert response.status_code == 404
    assert "Страница не найдена" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize("query", ["status=abc", "status=4", "sort=__class__"])
def test_bad_filters(client, state, query):
    assert client.get("/projects/?" + query).status_code == 400


@pytest.mark.django_db
def test_bad_date(client, state):
    assert client.get("/available/?date=2026-02-30").status_code == 400


@pytest.mark.django_db
def test_search_and_sort(client, state):
    response = client.get("/projects/?q=django&status=2&sort=-deadline")
    assert [p.pk for p in response.context["projects"]] == [1]
    response = client.get("/projects/?q=НЕСУЩЕСТВУЮЩЕЕ")
    assert "Проекты не найдены." in response.content.decode()


@pytest.mark.django_db
def test_pagination_preserves_filters(client, state):
    for i in range(7):
        p = Project.objects.create(
            name=f"Тест {i}", developer_id=1, status_id=2, deadline="2026-12-20"
        )
        p.technologies.add(1)
    response = client.get("/projects/?q=Тест&status=2&sort=name&page=2")
    assert len(response.context["projects"]) == 2
    assert "status=2" in response.context["params"]
    assert "sort=name" in response.context["params"]


@pytest.mark.django_db
def test_transitions_and_generated_field(state):
    with pytest.raises(ValidationError):
        p = Project.objects.get(pk=2)
        p.status_id = 3
        p.save()
    state.change_status(3)
    state.refresh_from_db()
    assert state.is_completed is True
    assert Project.objects.completed().count() == 1
    assert Project.objects.overdue(date(2026, 11, 6)).count() == 1
    with pytest.raises(ValueError):
        state.change_status(2)


@pytest.mark.django_db
def test_required_technology_and_protected_owner(state):
    with pytest.raises(ProtectedError):
        state.developer.delete()
    p = Project.objects.get(pk=2)
    with pytest.raises(ValidationError):
        p.technologies.clear()


@pytest.mark.django_db
def test_crud_form_admin_and_csrf(client, admin_client, state):
    assert client.get("/projects/new/").status_code == 302
    assert admin_client.get("/projects/new/").status_code == 200
    response = admin_client.post(
        "/projects/new/",
        {
            "name": "Новый проект",
            "developer": 1,
            "technologies": [1],
            "status": 1,
            "deadline": "2026-12-31",
        },
    )
    assert response.status_code == 302
    p = Project.objects.get(name="Новый проект")
    assert p.technologies.count() == 1
    p.delete()
    assert not Project.objects.filter(name="Новый проект").exists()
    assert admin_client.get("/admin/tracker/project/").status_code == 200


@pytest.mark.django_db
def test_empty_technology_form_rejected(admin_client, state):
    response = admin_client.post(
        "/projects/new/",
        {
            "name": "Нет технологий",
            "developer": 1,
            "status": 1,
            "deadline": "2026-12-31",
        },
    )
    assert response.status_code == 200
    assert not Project.objects.filter(name="Нет технологий").exists()


@pytest.mark.django_db
def test_slug_queries_and_statistics(client, state):
    assert client.get(state.get_absolute_url()).status_code == 200
    result = examples()
    assert result["aggregate"]["total"] == 2
    assert len(result["overdue"]) == 1
    response = client.get("/statistics/")
    assert response.context["stats"]["Всего проектов"] == 2
    assert response.context["stats"]["Завершен"] == 0


@pytest.mark.django_db
def test_eager_loading_reduces_queries(state):
    with CaptureQueriesContext(connection) as before:
        for p in Project.objects.all():
            str(p.developer), str(p.status), list(p.technologies.all())
    with CaptureQueriesContext(connection) as after:
        for p in Project.objects.with_related():
            str(p.developer), str(p.status), list(p.technologies.all())
    assert len(after) == 2
    assert len(before) > len(after)


@pytest.mark.django_db
def test_availability_excludes_completed(client, state):
    response = client.get("/available/?date=2026-12-31")
    assert list(response.context["items"]) == []
    state.change_status(3)
    response = client.get("/available/?date=2026-12-31")
    assert [p.pk for p in response.context["items"]] == [1]


@pytest.mark.django_db
def test_failed_save_shows_form_error(admin_client, state, monkeypatch):
    from django.db import DatabaseError
    from tracker.forms import ProjectForm

    def fail(*args, **kwargs):
        raise DatabaseError("test error")

    monkeypatch.setattr(ProjectForm, "save", fail)
    response = admin_client.post(
        "/projects/new/",
        {
            "name": "Не сохранять",
            "developer": 1,
            "technologies": [1],
            "status": 1,
            "deadline": "2026-12-31",
        },
    )
    assert response.status_code == 200
    assert "Не удалось сохранить" in response.content.decode()
    assert not Project.objects.filter(name="Не сохранять").exists()
