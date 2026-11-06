"""ПР1: оценка одного программного проекта."""
from datetime import date


def days_remaining(deadline: str, today: date) -> int:
    """Количество дней до срока; отрицательное означает просрочку."""
    return (date.fromisoformat(deadline) - today).days


def can_start(developer: str, technology: str) -> bool:
    """Для старта требуются ответственный и технология."""
    return bool(developer.strip() and technology.strip())


def get_project_status(completed: bool, started: bool) -> str:
    """Получить статус по состоянию проекта."""
    if completed:
        return 'Завершен'
    if started:
        return 'В работе'
    return 'Запланирован'


def main() -> None:
    name = 'Система учета программных проектов'
    developer = 'Анна Смирнова'
    technology = 'Python'
    deadline = '2026-12-20'
    estimated_hours = int('120')
    hourly_rate = float('500.0')
    completed = False
    started = can_start(developer, technology)
    print(f'Проект: {name}')
    print(f'Ответственный: {developer}; технология: {technology}')
    print(f'Оценка трудозатрат: {estimated_hours} ч')
    print(f'Оценка стоимости: {estimated_hours * hourly_rate:.2f} руб.')
    print(f'До срока: {days_remaining(deadline, date.today())} дней')
    print(f'Статус: {get_project_status(completed, started)}')


if __name__ == '__main__':
    main()
