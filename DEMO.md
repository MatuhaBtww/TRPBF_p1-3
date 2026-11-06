# Демонстрация проекта

1. Откройте VS Code. Выберите Файл → Открыть папку → C:\Users\Матвей\Documents\project_tracker.
2. Нажмите Ctrl+Shift+P → Python: Select Interpreter → .venv\Scripts\python.exe.
3. Выберите Терминал → Создать терминал. Введите .\.venv\Scripts\python.exe manage.py runserver.
4. В браузере откройте http://127.0.0.1:8000/projects/ . Покажите два исходных проекта.
5. В поле поиска введите Django. Объясните: поиск использует Q и связанные технологии.
6. Выберите статус «В работе». В tracker/views.py откройте project_list:
   QuerySet фильтруется, сортируется, затем Paginator делит его на страницы.
   В исходных данных только два проекта; дополнительные страницы демонстрирует test_pagination_preserves_filters.
7. Откройте карточку проекта. В tracker/models.py покажите ForeignKey и ManyToManyField.
   developer и status — связи многие к одному; technologies — многие ко многим.
8. Откройте templates/base.html, projects.html и includes/project_card.html.
   Объясните extends, block и include. Данные передаются из view через словарь контекста.
9. Откройте /statistics/: количество определяется Count; завершенные не включаются в просрочку.
10. Откройте /available/, выберите дату. Объясните точный смысл показателя из README.
11. Создайте суперпользователя командой из README. В /admin/ покажите список проектов,
    поиск, фильтр по статусу, сортировку и карточку разработчика со связанными проектами.
12. В tracker/models.py покажите change_status: сначала проверка rules.validate_transition,
    затем сохранение в транзакции. is_completed вычисляется SQLite по status_id.
13. Откройте tracker/migrations/0002_admin_features.py: RunPython сохраняет связи,
    заполняет code и slug для старых записей. get_absolute_url возвращает адрес по slug.
14. Откройте вкладку Debug Toolbar → SQL. Покажите SELECT и JOIN списка.
    select_related загружает ответственного и статус одним запросом;
    prefetch_related получает технологии отдельным запросом для всего списка.
15. Для тестов откройте второй терминал кнопкой + и запустите команды проверки из README.
    В tests/test_web.py откройте test_eager_loading_reduces_queries и test_transitions_and_generated_field.
    В первом тесте сравнивается число запросов для одинаковых данных;
    во втором проверяются разрешенный переход, запрет обратного перехода и вычисляемое поле.
16. Для ПР7 откройте sql/schema.sql: первичные ключи, внешние ключи, связующая таблица.
    В sql/queries.sql покажите WHERE, JOIN, COUNT, GROUP BY, HAVING и NOT IN.
17. Откройте tests/test_models.py и main.py: это сохраненная версия объектной модели и консольного меню.
18. Историю покажите командой git log --oneline --decorate. Поясните назначение тегов PR5–PR10.

Снимки интерфейса и результаты проверок находятся в отчетах и verification.txt.
Для отправки преподавателю используйте отчеты с вашим именем. Прохождение материалов
Яндекс Практикума подтверждается отдельно в личном кабинете.
