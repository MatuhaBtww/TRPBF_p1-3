"""Консольный интерфейс; предметные операции находятся в service.py."""
from datetime import date
from pathlib import Path

from service import (add_project, add_reference, change_status, decode,
                     describe_project, describe_reference, encode,
                     select_projects, statistics)
from storage import read_json, write_json

DATA_DIR = Path(__file__).resolve().parent / 'data'


def show_references(state: dict) -> None:
    for kind in ('developers', 'technologies', 'statuses'):
        print(kind + ':')
        for item in state[kind]:
            print('  ' + describe_reference(item))


def main() -> None:
    path = DATA_DIR / 'runtime.json'
    source = path if path.exists() else DATA_DIR / 'seed.json'
    try:
        state = decode(read_json(source))
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'Ошибка загрузки: {error}. Файл не изменен.')
        return
    print('Система учета программных проектов')
    while True:
        try:
            print('\n1 Список  2 Поиск  3 Добавить проект  4 Статус')
            print('5 Статистика  6 Справочники  7 Разработчик')
            print('8 Технология  9 Фильтр по статусу  0 Сохранить и выйти')
            action = input('Действие: ').strip()
            if action == '0':
                write_json(path, encode(state))
                print('Данные сохранены.')
                return
            if action in ('1', '2', '9'):
                query = input('Название: ') if action == '2' else ''
                status = int(input('ID статуса: ')) if action == '9' else None
                if status is not None and status not in (1, 2, 3):
                    raise ValueError('Неизвестный статус')
                projects = select_projects(state, query, status)
                for project in projects:
                    print(describe_project(project))
                if not projects:
                    print('Проекты не найдены.')
            elif action == '3':
                show_references(state)
                name = input('Название проекта: ')
                developer = int(input('ID ответственного: '))
                techs = [int(i) for i in input(
                    'ID технологий через запятую: ').split(',')]
                deadline = input('Срок (ГГГГ-ММ-ДД): ')
                new_id = add_project(state, name, developer, techs, deadline)
                print(f'Создан проект #{new_id}')
            elif action == '4':
                project_id = int(input('ID проекта: '))
                target = int(input('Статус: 1 план, 2 работа, 3 завершен: '))
                change_status(state, project_id, target)
                print('Статус изменен.')
            elif action == '5':
                for name, count in statistics(state, date.today()).items():
                    print(f'{name}: {count}')
            elif action == '6':
                show_references(state)
            elif action in ('7', '8'):
                kind = 'developers' if action == '7' else 'technologies'
                new_id = add_reference(state, kind, input('Имя/название: '))
                print(f'Добавлена запись #{new_id}')
            else:
                print('Неизвестная команда.')
        except (ValueError, KeyError, TypeError, OSError) as error:
            print(f'Ошибка: {error}')
        except (EOFError, KeyboardInterrupt):
            print('\nРабота прервана. Несохраненные изменения потеряны.')
            return


if __name__ == '__main__':
    main()
