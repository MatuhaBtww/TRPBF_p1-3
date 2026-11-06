from datetime import date
from pathlib import Path

import pytest

from rules import can_start, days_remaining, get_project_status
from service import (add_project, add_reference, change_status, decode,
                     describe_project, encode, select_projects, statistics)
from storage import read_json, write_json


@pytest.fixture
def state():
    path = Path(__file__).resolve().parents[1] / 'data' / 'seed.json'
    return decode(read_json(path))


def test_pr1_functions():
    assert days_remaining('2026-09-30', date(2026, 9, 23)) == 7
    assert can_start('Анна', 'Python')
    assert not can_start(' ', 'Python')
    assert get_project_status(True, True) == 'Завершен'


def test_add_project(state):
    new_id = add_project(state, 'API', 1, [1], '2027-01-01')
    assert new_id == 3
    assert encode(state)['projects'][-1]['name'] == 'API'


def test_search_case_insensitive(state):
    found = select_projects(state, 'ОТЧЕТОВ')
    assert len(found) == 1
    assert 'Сервис отчетов' in describe_project(found[0])


def test_sort_and_filter(state):
    assert 'Сервис отчетов' in describe_project(select_projects(state)[0])
    assert len(select_projects(state, status_id=2)) == 1


def test_status_transition(state):
    change_status(state, 2, 2)
    change_status(state, 2, 3)
    assert encode(state)['projects'][1]['status_id'] == 3


def test_invalid_transition_is_atomic(state):
    before = encode(state)
    with pytest.raises(ValueError):
        change_status(state, 2, 3)
    assert encode(state) == before


@pytest.mark.parametrize('developer, techs, deadline', [
    (999, [1], '2026-09-30'), (1, [999], '2026-09-30'),
    (1, [], '2026-09-30'), (1, [1, 1], '2026-09-30'),
    (1, [1], '2026-02-30'),
])
def test_invalid_project_does_not_mutate(state, developer, techs, deadline):
    before = encode(state)
    with pytest.raises(ValueError):
        add_project(state, 'Ошибка', developer, techs, deadline)
    assert encode(state) == before


def test_statistics_excludes_completed(state):
    today = date(2026, 9, 23)
    assert statistics(state, today)['Просрочено'] == 1
    change_status(state, 2, 2)
    change_status(state, 2, 3)
    assert statistics(state, today)['Просрочено'] == 0


def test_references(state):
    assert add_reference(state, 'technologies', 'PostgreSQL') == 3
    with pytest.raises(ValueError):
        add_reference(state, 'technologies', 'python')


def test_round_trip(state, tmp_path):
    path = tmp_path / 'projects.json'
    write_json(path, encode(state))
    restored = decode(read_json(path))
    assert encode(restored) == encode(state)


def test_broken_reference_rejected(state):
    raw = encode(state)
    raw['projects'][0]['developer_id'] = 999
    with pytest.raises(ValueError):
        decode(raw)


def test_duplicate_id_rejected(state):
    raw = encode(state)
    raw['developers'][1]['id'] = 1
    with pytest.raises(ValueError):
        decode(raw)


def test_corrupt_json_not_overwritten(tmp_path):
    path = tmp_path / 'broken.json'
    path.write_text('{broken', encoding='utf-8')
    with pytest.raises(ValueError):
        read_json(path)
    assert path.read_text(encoding='utf-8') == '{broken'


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_json(tmp_path / 'missing.json')


def test_empty_name(state):
    with pytest.raises(ValueError):
        add_project(state, ' ', 1, [1], '2026-09-30')
