"""ПР2: операции над списками словарей."""
from copy import deepcopy
from datetime import date
from typing import Iterator

from rules import (STATUS_NAMES, can_start, days_remaining,
                   get_project_status, validate_name, validate_transition)
from validation import validate_data


def decode(data: dict) -> dict:
    validate_data(data)
    return deepcopy(data)


def encode(state: dict) -> dict:
    validate_data(state)
    return deepcopy(state)


def get_item(state: dict, kind: str, item_id: int) -> dict:
    for item in state[kind]:
        if item['id'] == item_id:
            return item
    raise ValueError(f'Не найден {kind}: {item_id}')


def add_reference(state: dict, kind: str, name: str) -> int:
    if kind not in ('developers', 'technologies'):
        raise ValueError('Нельзя изменять этот справочник')
    name = validate_name(name)
    if any(r['name'].casefold() == name.casefold() for r in state[kind]):
        raise ValueError('Запись с таким именем уже существует')
    new_id = max((r['id'] for r in state[kind]), default=0) + 1
    state[kind].append({'id': new_id, 'name': name})
    return new_id


def add_project(state: dict, name: str, developer_id: int,
                technology_ids: list[int], deadline: str) -> int:
    name = validate_name(name)
    date.fromisoformat(deadline)
    developer = get_item(state, 'developers', developer_id)
    techs = [get_item(state, 'technologies', i) for i in technology_ids]
    if not techs or len(set(technology_ids)) != len(technology_ids):
        raise ValueError('Нужны неповторяющиеся технологии')
    if not can_start(developer['name'], techs[0]['name']):
        raise ValueError('Проект не готов к работе')
    new_id = max((p['id'] for p in state['projects']), default=0) + 1
    state['projects'].append({
        'id': new_id, 'name': name, 'developer_id': developer_id,
        'technology_ids': list(technology_ids), 'deadline': deadline,
        'status_id': 1,
    })
    return new_id


def change_status(state: dict, project_id: int, target: int) -> None:
    project = get_item(state, 'projects', project_id)
    validate_transition(project['status_id'], target)
    project['status_id'] = target


def select_projects(state: dict, query: str = '',
                    status_id: int | None = None) -> list[dict]:
    selected = [p for p in state['projects']
                if query.casefold() in p['name'].casefold()
                and (status_id is None or p['status_id'] == status_id)]
    return sorted(selected, key=lambda p: p['deadline'])


def overdue_projects(state: dict, today: date) -> Iterator[dict]:
    for project in state['projects']:
        if (project['status_id'] != 3
                and days_remaining(project['deadline'], today) < 0):
            yield project


def statistics(state: dict, today: date) -> dict[str, int]:
    result = {name: 0 for name in STATUS_NAMES.values()}
    for project in state['projects']:
        result[STATUS_NAMES[project['status_id']]] += 1
    result['Просрочено'] = sum(1 for _ in overdue_projects(state, today))
    return result


def describe_project(project: dict) -> str:
    status = get_project_status(project['status_id'] == 3,
                                project['status_id'] == 2)
    return (f"#{project['id']} {project['name']} | {status} | "
            f"срок {project['deadline']}")


def describe_reference(item: dict) -> str:
    return f"{item['id']}: {item['name']}"
