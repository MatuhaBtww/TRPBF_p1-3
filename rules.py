"""Правила, общие для функциональной и объектной версий."""
from datetime import date

STATUS_NAMES = {1: 'Запланирован', 2: 'В работе', 3: 'Завершен'}


def days_remaining(deadline: str, today: date) -> int:
    return (date.fromisoformat(deadline) - today).days


def can_start(developer: str, technology: str) -> bool:
    return bool(developer.strip() and technology.strip())


def get_project_status(completed: bool, started: bool) -> str:
    if completed:
        return STATUS_NAMES[3]
    if started:
        return STATUS_NAMES[2]
    return STATUS_NAMES[1]


def validate_name(name: str) -> str:
    if not isinstance(name, str) or not name.strip():
        raise ValueError('Название не может быть пустым')
    return name.strip()


def validate_id(value: int) -> None:
    if type(value) is not int or value < 1:
        raise ValueError('ID должен быть положительным целым числом')


def validate_transition(current: int, target: int) -> None:
    allowed = {1: {2}, 2: {1, 3}, 3: set()}
    if target not in allowed.get(current, set()):
        raise ValueError('Недопустимый переход статуса')
