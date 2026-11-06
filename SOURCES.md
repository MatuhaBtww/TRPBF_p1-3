# Источники требований и технических решений

ПР5_Django_Base.pdf: разделы 5.2–5.6, чек-лист 7.2 (с. 45), отчет 7.4 (с. 46).
ПР6_Django_Shablony_кор.pdf: шаблоны и static (с. 13–14), чек-лист (с. 51–52).
ПР7_Django_SQL.pdf: SQL-слой, импорт и запросы (раздел 5), чек-лист (с. 45–46).
PR9_Django_ORM_modeli.pdf: модели и ORM (раздел 5), чек-лист (с. 69–70).
PR10_Django_ORM_Admin.pdf: разделы 5.2–5.4, сводная таблица (с. 172), чек-лист (с. 174), отчет (с. 179–180).
Оригиналы PDF находятся в Downloads; номера страниц проверены по тексту PDF.
Roomly — учебный пример в методичках. Его помещения и бронирования не добавлялись в предметную область проекта.

Официальная документация:
- https://docs.djangoproject.com/en/5.2/releases/5.2/ — совместимость Python 3.14 начиная с Django 5.2.8.
- https://docs.djangoproject.com/en/5.2/ref/models/fields/ — ForeignKey, ManyToManyField, GeneratedField, SlugField.
- https://django-debug-toolbar.readthedocs.io/en/latest/installation.html — подключение панели отладки.

Фактические результаты: verification.txt, data/seed.json, миграции и tests/.
Проверка переноса сравнивает поля, идентификаторы и связи с исходным JSON.
Отчеты оформлены по предоставленным ПР1 и ПР2; сведения об авторе образцов удалены.
