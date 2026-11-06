# Соответствие индивидуальным заданиям

Сверка охватывает индивидуальную часть всех пяти предоставленных методичек.
Номера строк таблиц соответствуют пунктам чек-листа 7.2 каждого задания.
Источники и номера страниц приведены в SOURCES.md.

Применяется предметная область «Система учета программных проектов».
Упоминания Roomly в методичках задают образец приемов, а не требование добавлять
помещения и бронирования. Список и карточка помещения адаптированы к проекту,
вторая сущность — разработчик; отмена/завершение — к исходным правилам статусов ПР3.
Пример вычисляемой вместимости заменен признаком завершения, а выборка доступности
получила точное определение по срокам, приведенное в README.

Требования ранних этапов показываются по тегам PR5/PR6/PR7. В текущем приложении
источник данных уже ORM, как требуется на ПР9–ПР10. JSON, исходная объектная модель
и отдельная SQL-реализация сохранены.

## ПР5

| № | Требование | Реализация и подтверждение |
|---|---|---|
| 1 | Продолжение ПР3 | Исходные main.py, models.py, service.py, rules.py, storage.py, validation.py, JSON и тесты; контрольная точка PR3 |
| 2 | Django-проект | config/, manage.py |
| 3 | Django-приложение | tracker/, tracker/apps.py |
| 4 | Регистрация приложения | config/settings.py: INSTALLED_APPS |
| 5 | Маршрутизация | config/urls.py, tracker/urls.py |
| 6 | Ошибка 404 | handler404, not_found, templates/404.html; test_404 |
| 7 | View-функции | tracker/views.py |
| 8 | Главная | home; templates/home.html |
| 9 | Страницы предметной области | Проекты, разработчики, технологии, статистика |
| 10 | Динамические URL | Конвертеры int и slug; карточки |
| 11 | Навигация | templates/includes/nav.html |
| 12 | HTML | templates/; на этапе PR5 — HttpResponse/page |
| 13 | CSS и Bootstrap | static/style.css; Bootstrap 5.3.3 в base.html |
| 14 | Предметная область | Проект, разработчик, технология, статус; без сущностей Roomly |
| 15 | Запуск | setup.ps1, run.bat; HTTP-проверки |
| 16 | Проверка URL | test_pages, test_404 |
| 17 | README | README.md: открытие, установка, сценарии, проверки |
| 18 | pytest и flake8 | verification.txt; tests/ |
| 19 | Контрольная точка Git | Коммит и тег PR5 |

## ПР6

| № | Требование | Реализация и подтверждение |
|---|---|---|
| 1 | Продолжение ПР1–ПР5 | Тег PR5 и дальнейшая история |
| 2 | templates и DIRS | config/settings.py, templates/ |
| 3 | Базовый шаблон | templates/base.html |
| 4 | extends | Дочерние страницы |
| 5 | block | base.html: title/content |
| 6 | include | nav, project_card, pagination, project_table |
| 7 | Отдельная навигация | includes/nav.html |
| 8 | Список основной сущности | projects.html |
| 9 | Подробная страница основной сущности | detail.html |
| 10 | Список второй сущности | references.html: разработчики |
| 11 | Подробная страница второй сущности | developer.html |
| 12 | context | Словари в views.py |
| 13 | for | Списки и карточки |
| 14 | if | Права, статусы, пагинация |
| 15 | Пустой список | empty в шаблонах; test_empty_state_and_zero_groups |
| 16 | app_name | tracker/urls.py |
| 17 | Именованные URL | name в path |
| 18 | url в шаблонах | Навигация, кнопки, карточки |
| 19 | namespace | tracker:* и admin:* |
| 20 | Фильтры | date и default в шаблонах |
| 21 | Свой CSS | static/style.css |
| 22 | Изображение | static/logo.svg |
| 23 | JavaScript | static/app.js |
| 24 | Удаление page() из веб-представлений | Начиная с тега PR6: render() |
| 25 | Основные страницы | test_pages |
| 26 | Существующая модель объектов | На этапе PR6: tracker/repository.py и service.decode |
| 27 | JSON сохранен | data/seed.json; исходные модули |
| 28 | Нет преждевременного ORM | В теге PR6 нет tracker/models.py; ORM добавлен в PR9 |
| 29 | README обновлен | README.md |
| 30 | Django check | verification.txt |
| 31 | pytest | verification.txt |
| 32 | flake8 | verification.txt |
| 33 | Контрольная точка Git | Коммит и тег PR6 |

## ПР7

| № | Требование | Реализация и подтверждение |
|---|---|---|
| 1 | Продолжение ПР1–ПР6 | Тег PR6 и дальнейшая история |
| 2 | Сущности | Проект, разработчик, технология, статус |
| 3 | Таблицы | sql/schema.sql: 4 сущности и промежуточная таблица |
| 4 | Поля и типы | INTEGER, TEXT, обязательность и CHECK |
| 5 | Первичные ключи | id INTEGER PRIMARY KEY; составной PK в project_technologies |
| 6 | Внешние ключи | developer_id, status_id, project_id, technology_id |
| 7 | Файл SQLite | data/legacy.sqlite3; создается импортом |
| 8 | SQL-схема | sql/schema.sql |
| 9 | Подключение | db/database.py: connect |
| 10 | Проверка FK | PRAGMA foreign_keys=ON; foreign_key_check в db/check_queries.py |
| 11 | Скрипт переноса | db/import_json.py |
| 12 | Перенос JSON | import_data; test_sql_import_queries_and_constraints |
| 13 | Проверка переноса | Поля, количества и связи; исходный JSON не меняется |
| 14 | Файл SQL-запросов | sql/queries.sql |
| 15 | SQLite CLI | db/check_queries.py; sql_verification.json |
| 16 | SELECT и WHERE | Запросы 1, 2, 11 |
| 17 | JOIN | Запросы 3, 4 |
| 18 | Агрегаты | Запросы 5, 6 |
| 19 | GROUP BY | Запросы 7, 8, 12 |
| 20 | HAVING | Запрос 8 |
| 21 | Параметры ? | db/queries.py; db/import_json.py |
| 22 | sqlite3.Row | db/database.py; SQL-представления тега PR7 |
| 23 | Список основной сущности из SQLite | Тег PR7: list_projects и sql_projects.html |
| 24 | Список второй сущности из SQLite | Тег PR7: state() читает разработчиков из SQLite |
| 25 | Выборка по дате с подзапросом | available_developers: без незавершенных проектов со сроком <= выбранной даты |
| 26 | Статистика | db/queries.statistics; страница /statistics/ |
| 27 | Навигация | Общий шаблон |
| 28 | README | Команды SQL-этапа |
| 29 | Проверки | SQL CLI + pytest; verification.txt, sql_verification.json |
| 30 | Контрольная точка Git | Коммит и тег PR7 |
| 31 | Минимум 10 SQL и по 2 каждого вида | 12 запросов; WHERE 1/2, JOIN 3/4, агрегаты 5/6, GROUP BY 7/8; каждый выполнен |

## ПР9

| № | Требование | Реализация и подтверждение |
|---|---|---|
| 1 | Продолжение проекта | Тег PR7 и дальнейшая история |
| 2 | Модели предметной области | tracker/models.py: Developer, Technology, Status, Project |
| 3 | Поля моделей | CharField, DateField, FK, M2M, SlugField |
| 4 | Обязательность и ограничения | full_clean, UniqueConstraint, CheckConstraint, формы |
| 5 | Первичные ключи | Автоматический id; ID исходных записей сохраняются импортом |
| 6 | Связи ORM | ForeignKey и ManyToManyField |
| 7 | on_delete и related_name | PROTECT; projects; технологии через M2M |
| 8 | Миграции созданы | tracker/migrations/0001–0003 |
| 9 | Миграции применены | migrate; verification.txt |
| 10 | Обратные связи | developer.projects; technology.projects; страницы и inline |
| 11 | Наборы объектов | all, filter в queries.py |
| 12 | Отдельный объект | get_object_or_404 в карточках; get в orm_examples |
| 13 | Создание изменение удаление | Формы проекта и справочников; Admin; CRUD-тесты |
| 14 | Одно условие | planned/in_progress/completed |
| 15 | Несколько условий | Поиск + статус + срок + разработчик + технология |
| 16 | Поля связанных моделей | developer__name, technologies__name |
| 17 | exclude | QuerySet.active; available_developers |
| 18 | Поиск строки | icontains |
| 19 | Поиск нескольких полей | Q с OR в filtered_projects |
| 20 | Сортировка | SORT_FIELDS: срок, название, разработчик; белый список |
| 21 | Связанные данные без N+1 | with_related, select_related, prefetch_related |
| 22 | Выбор полей | project_rows: values; таблица и CSV |
| 23 | Агрегаты | summary: aggregate + Count/Min/Max |
| 24 | Аннотации и группировка | project_rows: F; developer_totals и technology_totals: Count |
| 25 | Paginator | project_list; 5 записей на страницу |
| 26 | Сохранение условий при переходе | GET.urlencode; pagination.html; test_pagination_preserves_filters |
| 27 | Интеграция ORM | Все текущие предметные веб-представления |
| 28 | Пустые/ошибочные/отсутствующие данные | Формы фильтров, empty, 400, 404, тесты |
| 29 | Проверка моделей и сценариев | pytest; check; миграционный тест |
| 30 | README и Git | README.md; коммит и тег PR9 |
| 31 | Минимум 15 выражений по категориям | ORM_CATALOG.md; queries.py и orm_examples.py; выполнение подтверждено verification.txt |

## ПР10

| № | Требование | Реализация и подтверждение |
|---|---|---|
| 1 | Регистрация и настройка моделей | admin.py: четыре модели, list_display, search_fields, list_filter, ordering, inline |
| 2 | Миграции схемы | 0002 и 0003; migrate/check |
| 3 | Преобразование старых статусов | 0002 RunPython: код Status.Code без изменения PK/FK; test_migration_1_to_3_preserves_data_slug_and_status_codes |
| 4 | Менеджер и QuerySet | active, completed, planned, in_progress, for_date, overdue, with_related |
| 5 | ORM в основной работе | queries.py и views.py |
| 6 | Фильтры сортировка пагинация | ProjectFilterForm, SORT_FIELDS, Paginator; совместная проверка |
| 7 | Доступность с учетом статуса | available_developers; завершенные проекты не блокируют разработчика |
| 8 | Статистика по статусам | summary и status_totals; исходные статусы ПР3 сохранены |
| 9 | slug и get_absolute_url | slug, reverse, маршрут by-slug; старый URL по id сохранен |
| 10 | Контекстный процессор | project_summary в settings и footer |
| 11 | GeneratedField | is_completed вычисляется SQLite; тест перехода статуса |
| 12 | Debug Toolbar и SQL | Режим run.bat debug; снимок SQL; сравнение 7 → 2 в тесте |
| 13 | Django Shell | orm_examples; verification.txt |
| 14 | check | verification.txt |
| 15 | Автотесты | verification.txt, tests/ |
| 16 | README | Установка, открытие в VS Code, вход, сценарии, проверки |
| 17 | Git | Истории объединены без перезаписи; изменения публикуются в main |

## Дополнительные пункты практической части ПР10

| Раздел | Реализация и проверка |
|---|---|
| 5.2.1 | Постоянный matvey, реальный вход и повторный вход; bootstrap_admin не сбрасывает пароль |
| 5.2.2–5.2.3 | list_display_links, search_fields, list_filter, ordering, list_per_page; локализация |
| 5.2.4 | Группа «Наблюдатели» и observer, только view-разрешения; проверены запреты add/change/delete |
| 5.2.5.1–5.2.5.3 | list_editable для срока; help_text с миграцией 0003; test_admin_deadline_editable_in_list |
| 5.2.5.4–5.2.5.5 | ProjectInline, readonly_fields для id/slug/is_completed |
| 5.2.5.6 | Аннотированное число незавершенных проектов разработчика, list_select_related |
| 5.2.5.7 | Три массовых действия через change_status, сообщения об измененных/пропущенных; date_hierarchy и autocomplete_fields |
| 5.3.1–5.3.4 | all/filter/exclude/get/order_by/values/aggregate, многопольный поиск Q |
| 5.3.5–5.3.6 | Основной список объектов загружает связи совместно; табличный список получает annotate(F)+values одним JOIN |
| 5.3.7–5.3.9 | Пользовательский QuerySet, F в рабочем табличном режиме/CSV, обратные связи |
| 5.3.10, 5.4.1–5.4.2 | SQL-панель для списка и карточки; сравнение одинаковых выборок до/после eager loading |
| 5.4.3 | TextChoices в существующем Status, миграция данных без потери связей, QuerySet использует константы |
| 5.4.4–5.4.6 | GeneratedField, slug и get_absolute_url, контекстный процессор |

Контрольные результаты находятся в verification.txt и sql_verification.json.
Ручные проверки браузера описаны в browser_verification.json. Отчеты с фактическими
снимками интерфейса находятся в reports/.
