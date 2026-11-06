"""ПР3: те же операции над коллекциями объектов."""
from datetime import date
from typing import Iterator

from models import Developer, NamedEntity, Project, Status, Technology
from rules import STATUS_NAMES, validate_name
from validation import validate_data


def decode(data: dict) -> dict:
    validate_data(data)
    state = {
        'developers': [Developer.from_data(r) for r in data['developers']],
        'technologies': [Technology.from_data(r)
                         for r in data['technologies']],
        'statuses': [Status.from_data(r) for r in data['statuses']],
        'projects': [],
    }
    for row in data['projects']:
        state['projects'].append(Project(
            row['id'], row['name'],
            get_item(state, 'developers', row['developer_id']),
            [get_item(state, 'technologies', i)
             for i in row['technology_ids']], row['deadline'],
            get_item(state, 'statuses', row['status_id']),
        ))
    return state


def encode(state: dict) -> dict:
    data = {kind: [{'id': r.id, 'name': r.name} for r in state[kind]]
            for kind in ('developers', 'technologies', 'statuses')}
    data['projects'] = [
        {'id': p.id, 'name': p.name, 'developer_id': p.developer.id,
         'technology_ids': [t.id for t in p.technologies],
         'deadline': p.deadline, 'status_id': p.status.id}
        for p in state['projects']
    ]
    validate_data(data)
    return data


def get_item(state: dict, kind: str, item_id: int) -> NamedEntity | Project:
    for item in state[kind]:
        if item.id == item_id:
            return item
    raise ValueError(f'Не найден {kind}: {item_id}')


def add_reference(state: dict, kind: str, name: str) -> int:
    classes = {'developers': Developer, 'technologies': Technology}
    if kind not in classes:
        raise ValueError('Нельзя изменять этот справочник')
    name = validate_name(name)
    if any(r.name.casefold() == name.casefold() for r in state[kind]):
        raise ValueError('Запись с таким именем уже существует')
    new_id = max((r.id for r in state[kind]), default=0) + 1
    state[kind].append(classes[kind](new_id, name))
    return new_id


def add_project(state: dict, name: str, developer_id: int,
                technology_ids: list[int], deadline: str) -> int:
    new_id = max((p.id for p in state['projects']), default=0) + 1
    project = Project(
        new_id, name, get_item(state, 'developers', developer_id),
        [get_item(state, 'technologies', i) for i in technology_ids],
        deadline, get_item(state, 'statuses', 1),
    )
    state['projects'].append(project)
    return new_id


def change_status(state: dict, project_id: int, target: int) -> None:
    project = get_item(state, 'projects', project_id)
    project.change_status(get_item(state, 'statuses', target))


def select_projects(state: dict, query: str = '',
                    status_id: int | None = None) -> list[Project]:
    selected = [p for p in state['projects']
                if query.casefold() in p.name.casefold()
                and (status_id is None or p.status.id == status_id)]
    return sorted(selected, key=lambda p: p.deadline)


def overdue_projects(state: dict, today: date) -> Iterator[Project]:
    for project in state['projects']:
        if project.status.id != 3 and project.days_remaining(today) < 0:
            yield project


def statistics(state: dict, today: date) -> dict[str, int]:
    result = {name: 0 for name in STATUS_NAMES.values()}
    for project in state['projects']:
        result[project.status.name] += 1
    result['Просрочено'] = sum(1 for _ in overdue_projects(state, today))
    return result


def describe_project(project: Project) -> str:
    return str(project)


def describe_reference(item: NamedEntity) -> str:
    return str(item)
