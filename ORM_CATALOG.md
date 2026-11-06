# ORM-выражения проекта

| Категория ПР9 | Выражения и реальное применение |
|---|---|
| Базовое получение, минимум 2 | Project.objects.all() для списка; get/get_object_or_404 для карточки |
| Фильтрация, минимум 4 | planned; статус и дата вместе; developer/technology; exclude завершенных |
| Поиск, минимум 2 | name__icontains; Q по названию, разработчику и технологиям |
| Сортировка, минимум 2 | name/deadline; developer__name + deadline + pk |
| Связи, минимум 2 | select_related(developer,status); prefetch_related(technologies); developer.projects |
| Агрегаты и аннотации, минимум 2 | summary aggregate Count/Min/Max; developer_totals Count с условием; F+values в таблице |
| Пагинация, минимум 1 | Paginator фильтрованного QuerySet в project_list |

В tracker/orm_examples.py функция examples() выполняет 21 отдельное выражение:
all, filter, and, related, exclude, search, or, not, sort, slice, first, get,
select_related, prefetch, values, aggregate, annotate, F, active, completed, overdue.
Она работает с существующими данными и не создает демонстрационных записей.
Основные сценарии этих категорий также используются в tracker/queries.py и views.py.
Подсчет 21 получен как число ключей результата examples(), а не число вызовов методов
внутри одного составного запроса. Проверка выполнения записана в verification.txt.
