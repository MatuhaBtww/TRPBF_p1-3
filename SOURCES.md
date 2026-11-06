# Источники требований

| Задание | Проверенные разделы |
|---|---|
| ПР5_Django_Base.pdf | 5.1–5.6; чек-лист 7.2, с. 45; отчет 7.4, с. 46 |
| ПР6_Django_Shablony_кор.pdf | Раздел 5; чек-лист 7.2, с. 51–52 |
| ПР7_Django_SQL.pdf | Раздел 5; требования и проверка SQL, с. 45–48 |
| PR9_Django_ORM_modeli.pdf | Минимумы ORM, с. 6–7; раздел 5; чек-лист, с. 69–70 |
| PR10_Django_ORM_Admin.pdf | 5.2–5.4; сводка, с. 172; чек-лист, с. 174; критерии и отчет, с. 175–180 |

Предметная область адаптирована к системе учета программных проектов.
Исходные сущности — проект, разработчик, технология, статус.
Сценарии помещений и бронирований из примера Roomly не добавляют новые сущности в этот проект.
Отсутствующие в исходной модели отмена бронирований и вместимость заменены подходящими
сценариями переходов статуса и вычисляемым признаком завершения проекта.
Показатель загрузки имеет точное определение в README.

Технические источники:

- https://docs.djangoproject.com/en/5.2/releases/5.2/
- https://docs.djangoproject.com/en/5.2/ref/models/fields/
- https://docs.djangoproject.com/en/5.2/ref/contrib/admin/
- https://docs.djangoproject.com/en/5.2/topics/forms/modelforms/
- https://docs.djangoproject.com/en/5.2/topics/auth/default/
- https://django-debug-toolbar.readthedocs.io/en/latest/installation.html

Сопоставление каждого пункта индивидуальных заданий с кодом приведено в REQUIREMENTS.md.
Фактические результаты — verification.txt, sql_verification.json и tests/.
