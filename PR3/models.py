from datetime import date

from rules import (STATUS_NAMES, can_start, days_remaining,
                   get_project_status, validate_id, validate_name,
                   validate_transition)


class NamedEntity:

    def __init__(self, entity_id: int, name: str) -> None:
        validate_id(entity_id)
        self.id = entity_id
        self.name = validate_name(name)

    @classmethod
    def from_data(cls, data: dict) -> 'NamedEntity':
        return cls(data['id'], data['name'])

    def __str__(self) -> str:
        return f'{self.id}: {self.name}'


class Developer(NamedEntity):
    """Разработчик является именованной сущностью."""

    def __str__(self) -> str:
        return f'{self.id}: Разработчик {self.name}'


class Technology(NamedEntity):
    """Технология программного проекта."""

    def __str__(self) -> str:
        return f'{self.id}: Технология {self.name}'


class Status(NamedEntity):
    """Один из трех допустимых статусов."""

    def __init__(self, entity_id: int, name: str) -> None:
        super().__init__(entity_id, name)
        if STATUS_NAMES.get(entity_id) != name:
            raise ValueError('Неизвестный статус')


class Project:

    def __init__(self, project_id: int, name: str, developer: Developer,
                 technologies: list[Technology], deadline: str,
                 status: Status) -> None:
        validate_id(project_id)
        self.id = project_id
        self.name = validate_name(name)
        self.deadline = date.fromisoformat(deadline).isoformat()
        if not isinstance(developer, Developer):
            raise ValueError('Требуется объект Developer')
        if not isinstance(status, Status):
            raise ValueError('Требуется объект Status')
        if not technologies or any(
            not isinstance(t, Technology) for t in technologies
        ):
            raise ValueError('Требуется список технологий')
        if len({t.id for t in technologies}) != len(technologies):
            raise ValueError('Повторная технология')
        self.developer = developer
        self.technologies = tuple(technologies)
        self._status = status
        if not self.can_start():
            raise ValueError('Проект не готов к работе')

    @property
    def status(self) -> Status:
        """Статус меняется только через метод change_status."""
        return self._status

    def change_status(self, target: Status) -> None:
        validate_transition(self.status.id, target.id)
        self._status = target

    def can_start(self) -> bool:
        return can_start(self.developer.name, self.technologies[0].name)

    def days_remaining(self, today: date) -> int:
        return days_remaining(self.deadline, today)

    def __str__(self) -> str:
        status = get_project_status(self.status.id == 3, self.status.id == 2)
        return (f'#{self.id} {self.name} | {status} | '
                f'срок {self.deadline}')
