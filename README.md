# Система учета программных проектов

Студент: Семин Матвей Романович, ЭФБО-10-24. Преподаватель: Ящун Т. В.
Репозиторий: https://github.com/MatuhaBtww/TRPBF_p1-3

Проект продолжает исходную консольную версию ПР3. Исходные main.py, models.py,
rules.py, service.py, storage.py, validation.py, JSON и тесты сохранены.
Веб-часть использует Django, ORM и SQLite. Запись доступна сотруднику после входа.

## Установка и запуск в PowerShell

Рабочая папка: C:\Users\Матвей\Documents\project_tracker

```powershell
Set-Location -LiteralPath 'C:\Users\Матвей\Documents\project_tracker'
powershell -ExecutionPolicy Bypass -File .\setup.ps1
.\.venv\Scripts\python.exe manage.py runserver
```

Откройте http://127.0.0.1:8000/projects/ . Остановка сервера: Ctrl+C в терминале.
После установки можно запускать двойным щелчком run.bat.
Python 3.14; точные версии библиотек записаны в requirements.txt.

## Администратор

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Укажите своё имя пользователя и пароль. Затем откройте /admin/.
В панели доступны проекты, разработчики, технологии и фиксированный справочник статусов.
Суперпользователь для ручной работы не создается автоматически.

## Страницы и сценарии

Главная /; описание /about/; проекты /projects/; карточка /projects/1/;
карточка по slug /projects/by-slug/project-1/; разработчики /developers/;
карточка разработчика /developers/1/; технологии /technologies/;
статистика /statistics/; загрузка разработчиков /available/.
Формы /projects/new/ и /projects/1/edit/ требуют входа сотрудника.
В списке работают поиск по проекту, разработчику и технологии, статус,
сортировка и пагинация по 5 записей с сохранением параметров.

Проект имеет одного ответственного, один статус и несколько технологий.
Переходы: Запланирован → В работе; В работе → Запланирован или Завершен.
Из завершенного проекта переходы запрещены. Правило реализовано в rules.py
и применяется в tracker/models.py. Формы требуют хотя бы одну технологию.
QuerySet.update() и прямой SQL обходят Python-валидацию; используйте формы,
save() и change_status(), когда меняете статус.

Загрузка показывает разработчиков без незавершенных проектов со сроком не позднее
выбранной даты. Проект не содержит дат начала работ, поэтому календарная занятость
не вычисляется. Это адаптация SQL-подзапроса к предметной области.

## Хранение и перенос данных

data/seed.json — исходные данные; main.py сохраняет консольные изменения в runtime.json.
Консоль и веб используют отдельные хранилища и автоматически не синхронизируются.
data/projects.sqlite3 — текущая ORM-база; data/legacy.sqlite3 — учебная SQL-база ПР7.
import_json выбирает runtime.json, если он существует, иначе seed.json, и сохраняет ID.
Повторный импорт в непустые предметные таблицы отменяется без перезаписи.
Для другого JSON: python manage.py import_json --source путь_к_файлу.
Перед любыми экспериментами скопируйте data/ в отдельную резервную папку.

## Проверки

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\python.exe -m flake8 .
.\.venv\Scripts\python.exe manage.py shell -c "from tracker.orm_examples import examples; print(examples())"
```

PASSED означает, что конкретный сценарий прошел; FAILED и ERROR требуют разбора.
Итоговый протокол текущей проверки хранится в verification.txt.
E501 исключен из flake8 для длинных строк SQL и HTML; остальные проверки активны.
Debug Toolbar включен только локально при DEBUG=1. Откройте боковую вкладку SQL.
Для отключения: $env:ENABLE_DEBUG_TOOLBAR='0'.

## Структура и история

config/ — настройки и маршруты; tracker/models.py — ORM;
tracker/views.py — HTTP-сценарии; tracker/forms.py — проверка форм;
tracker/admin.py — административная панель; tracker/migrations/ — схема и перенос полей;
templates/ — HTML; static/ — CSS, SVG и JavaScript;
db/ и sql/ — сохраненный учебный SQL-слой; tests/ — исходные и новые тесты.

Локальные теги PR3, PR5, PR6, PR7, PR9, PR10 отмечают этапы развития.
PR5 читает JSON и формирует HTTP-ответы; PR6 использует шаблоны;
PR7 читает SQLite через sqlite3; PR9 переходит к ORM; PR10 добавляет Admin,
TextChoices для кодов справочника статусов, миграцию данных, slug,
GeneratedField, контекстный процессор и Debug Toolbar.
Коммиты локальные; публикация на GitHub не выполнялась. Исходная папка не содержала .git,
поэтому локальная история начинается с предоставленной версии ПР3.
Не выполняйте git push --force. Перед публикацией сопоставьте историю с origin.

Для SQL-этапа: python -m db.import_json; запросы находятся в sql/queries.sql.
Импорт отменится, если legacy.sqlite3 уже заполнена. Запросы можно выполнять
в расширении SQLite: Ctrl+Shift+P → SQLite: Open Database → data/legacy.sqlite3.
Для проверки старых этапов используйте отдельный git worktree, отдельную .venv и
установку requirements.txt этого этапа. Не переключайте старые теги поверх текущей базы.

Инструкция по защите — DEMO.md. Источники требований — SOURCES.md.
