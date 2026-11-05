# Система учета программных проектов

ПР5: Django-проект config, приложение tracker. Данные читаются из JSON через объектную модель ПР3.

Установка: python -m pip install -r requirements.txt
Запуск: python manage.py runserver
Проверки: python manage.py check; python -m pytest

Адреса: /, /about/, /projects/, /projects/1/, /developers/, /developers/1/, /technologies/, /statistics/.
Консольная версия: python main.py.

ПР6: HTML перенесен в templates; base.html, extends, include, for/empty, if, url, фильтры, CSS, SVG и JavaScript. Источник данных остается JSON.

ПР7: python -m db.import_json переносит JSON в data/legacy.sqlite3. SQL-схема и 12 запросов в sql/. Веб-страницы читают SQLite. /available/ показывает разработчиков без незавершенных проектов со сроком до выбранной даты.
