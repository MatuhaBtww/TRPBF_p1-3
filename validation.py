"""Проверка структуры файла и ссылочной целостности."""
from datetime import date

from rules import STATUS_NAMES, validate_id, validate_name


def validate_data(data: dict) -> None:
    indexes = {}
    for key in ('developers', 'technologies', 'statuses', 'projects'):
        rows = data.get(key)
        if not isinstance(rows, list):
            raise ValueError(f'Отсутствует список {key}')
        ids = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError('Запись должна быть объектом JSON')
            validate_id(row['id'])
            validate_name(row['name'])
            if row['id'] in ids:
                raise ValueError(f'Повторный ID в {key}')
            ids.add(row['id'])
        indexes[key] = ids
    actual = {s['id']: s['name'] for s in data['statuses']}
    if actual != STATUS_NAMES:
        raise ValueError('Неверный справочник статусов')
    for project in data['projects']:
        date.fromisoformat(project['deadline'])
        for field, key in (('developer_id', 'developers'),
                           ('status_id', 'statuses')):
            validate_id(project[field])
            if project[field] not in indexes[key]:
                raise ValueError(f'Неизвестная ссылка: {field}')
        techs = project['technology_ids']
        if not isinstance(techs, list) or not techs:
            raise ValueError('Нужна хотя бы одна технология')
        for tech_id in techs:
            validate_id(tech_id)
            if tech_id not in indexes['technologies']:
                raise ValueError('Неизвестная технология')
        if len(techs) != len(set(techs)):
            raise ValueError('Технологии не должны повторяться')
