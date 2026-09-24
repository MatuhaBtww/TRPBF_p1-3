from datetime import date
from pathlib import Path

import pytest

from models import Developer, Project, Status, Technology
from service import decode, encode
from storage import read_json


def test_composition_and_methods():
    developer = Developer(1, 'Анна')
    technology = Technology(1, 'Python')
    project = Project(1, 'API', developer, [technology], '2026-09-30',
                      Status(1, 'Запланирован'))
    assert project.developer is developer
    assert project.technologies[0] is technology
    assert project.can_start()
    assert project.days_remaining(date(2026, 9, 23)) == 7
    assert 'API' in str(project)


def test_status_property_is_read_only():
    project = Project(1, 'API', Developer(1, 'Анна'),
                      [Technology(1, 'Python')], '2026-09-30',
                      Status(1, 'Запланирован'))
    with pytest.raises(AttributeError):
        project.status = Status(3, 'Завершен')


def test_polymorphism_and_classmethod():
    developer = Developer.from_data({'id': 1, 'name': 'Анна'})
    technology = Technology.from_data({'id': 1, 'name': 'Python'})
    assert isinstance(developer, Developer)
    assert 'Разработчик' in str(developer)
    assert 'Технология' in str(technology)


def test_json_restores_shared_references():
    path = Path(__file__).resolve().parents[1] / 'data' / 'seed.json'
    state = decode(read_json(path))
    restored = decode(encode(state))
    project = restored['projects'][0]
    assert isinstance(project, Project)
    assert project.developer is restored['developers'][0]
    assert project.technologies[0] is restored['technologies'][0]
    assert project.status is restored['statuses'][1]
