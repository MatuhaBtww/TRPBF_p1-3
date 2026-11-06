# Демонстрация преподавателю

## Подготовка

Откройте в VS Code папку `C:\Users\Матвей\Documents\project_tracker`.
Нажмите **Терминал → Создать терминал** и запустите `.\run.bat`.
В браузере откройте http://127.0.0.1:8000/ и войдите как `matvey`.
Пароль находится в `.private\admin-access.txt`.

## Показ приложения

1. На главной покажите сводку и ближайшие сроки. Объясните, какие проекты считаются просроченными.
2. В разделе **Проекты** найдите `Django`, выберите «В работе» и нажмите **Применить**.
3. Переключите список в таблицу и выгрузите CSV. Это одна и та же отфильтрованная выборка.
4. Создайте тестового разработчика и технологию, затем проект. Из плана переведите его в работу и завершите.
5. Покажите сообщение об ошибке для пустого названия или отсутствующей технологии.
6. В **Статистике** покажите статусы и распределение по разработчикам и технологиям.
7. В **Загрузке** выберите дату. Это разработчики без незавершенных проектов с наступившим к ней сроком, а не календарь рабочего времени.
8. Откройте **Администрирование → Проекты**: поиск, фильтры, редактирование срока в строке, массовые действия.
9. Откройте разработчика в Admin и покажите связанные проекты. Покажите подсказки и неизменяемые поля.
10. Выйдите и войдите как `observer`: списки доступны, добавление, изменение и удаление запрещены.
11. Если нужны дополнительные страницы списка, создайте несколько тестовых проектов. Не меняйте исходные записи для демонстрации. Удалите созданные тестовые проекты после показа.

## Что открыть в коде

| Тема | Файл и функция | Что объяснить |
|---|---|---|
| HTTP и URL | `config/urls.py`, `tracker/urls.py`, `project_detail()` | Адрес → обработчик → ответ; int/slug и 404 |
| Шаблоны | `templates/base.html`, `projects.html`, `includes/` | extends, block, include, context, циклы, условия, static |
| SQL ПР7 | `sql/schema.sql`, `sql/queries.sql`, `db/database.py` | PK, FK, промежуточная таблица, WHERE, JOIN, GROUP BY, HAVING, параметры ? |
| Модели | `tracker/models.py` | FK к разработчику и статусу, M2M к технологиям, abstract NamedEntity |
| Правила | `rules.validate_transition`, `Project.change_status` | Проверка разрешенного перехода перед записью в транзакции |
| ORM | `tracker/queries.py`, `tracker/orm_examples.py` | filter/exclude, Q, order_by, F+annotate+values, Count и aggregate |
| Пагинация | `project_list()`, `includes/pagination.html` | Paginator, сохранение GET-параметров, размер страницы |
| Admin | `tracker/admin.py` | list_display, list_editable, actions, inlines, права, list_select_related |
| Миграции | `tracker/migrations/0001*`, `0002*`, `0003*` | Создание схемы; перенос code и slug без потери ID и связей; help_text |
| Вычисления | `Project.is_completed`, `get_absolute_url()` | Признак вычисляется SQLite, адрес строится reverse по slug |
| Общий контекст | `tracker/context_processors.py` | Одни и те же общие значения на нескольких страницах |

## Проверки в отдельном терминале

```powershell
Set-Location -LiteralPath 'C:\Users\Матвей\Documents\project_tracker'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m flake8 .
.\.venv\Scripts\python.exe -m db.check_queries --cli 'C:\msys64\mingw64\bin\sqlite3.exe'
.\.venv\Scripts\python.exe manage.py shell -c "from tracker.orm_examples import examples; print(examples())"
```

Покажите итог `passed`, затем откройте выбранный тест:

- `test_import_preserves_all_data_and_links`: поля, идентификаторы и связи совпадают с JSON.
- `test_migration_1_to_3_preserves_data_slug_and_status_codes`: реальная миграция старой схемы сохраняет данные.
- `test_pagination_preserves_filters`: условия поиска и сортировки сохраняются на следующей странице.
- `test_replace_only_technology_in_form`: единственную технологию можно заменить без потери связи.
- `test_bootstrap_admin_persistent_idempotent_and_readonly_group`: пароль не сбрасывается, роль просмотра не меняет данные.
- `test_eager_loading_reduces_queries`: одинаковые данные получены с меньшим числом запросов.
- `test_failed_save_shows_form_error`: предусмотренная ошибка базы показана пользователю без аварийной страницы.

Для Debug Toolbar остановите обычный сервер и запустите `.\run.bat debug`.
В браузере откройте список и карточку проекта, затем вкладку **SQL**.
Найдите SELECT с JOIN для разработчика/статуса и отдельный prefetch технологий.
Для списка также ожидаются запросы COUNT пагинатора, фильтров и общего контекста.
Измерение 7 → 2 относится к сравнению загрузки двух исходных проектов в тесте,
а не к общему количеству запросов всей веб-страницы.

## История

`git log --oneline --decorate` показывает контрольные точки.
`REQUIREMENTS.md` связывает пункты заданий с реализацией и проверками.
Отчеты находятся в `reports/`; результат текущих проверок — в `verification.txt`.
