from datetime import date
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.functions import Lower
from django.urls import reverse

from rules import STATUS_NAMES, validate_name, validate_transition


class NamedEntity(models.Model):
    name = models.CharField(
        "Название",
        max_length=200,
        help_text="От 1 до 200 символов; пробелы по краям удаляются.",
    )

    class Meta:
        abstract = True
        ordering = ["name", "pk"]

    def clean(self):
        super().clean()
        try:
            self.name = validate_name(self.name)
        except ValueError as error:
            raise ValidationError({"name": str(error)})
        if self._meta.model_name in ("developer", "technology"):
            names = (
                type(self).objects.exclude(pk=self.pk).values_list("name", flat=True)
            )
            if any(name.casefold() == self.name.casefold() for name in names):
                raise ValidationError({"name": "Запись с таким именем уже существует."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Developer(NamedEntity):
    class Meta(NamedEntity.Meta):
        verbose_name = "Разработчик"
        verbose_name_plural = "Разработчики"
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_developer_name")
        ]


class Technology(NamedEntity):
    class Meta(NamedEntity.Meta):
        verbose_name = "Технология"
        verbose_name_plural = "Технологии"
        constraints = [
            models.UniqueConstraint(Lower("name"), name="unique_technology_name")
        ]


class Status(NamedEntity):
    class Code(models.TextChoices):
        PLANNED = "planned", "Запланирован"
        ACTIVE = "active", "В работе"
        COMPLETED = "completed", "Завершен"

    code = models.CharField("Код", max_length=12, choices=Code.choices, unique=True)

    class Meta(NamedEntity.Meta):
        ordering = ["pk"]
        verbose_name = "Статус"
        verbose_name_plural = "Статусы"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(pk__in=[1, 2, 3]), name="known_status_id"
            )
        ]

    def clean(self):
        super().clean()
        codes = {1: self.Code.PLANNED, 2: self.Code.ACTIVE, 3: self.Code.COMPLETED}
        if STATUS_NAMES.get(self.pk) != self.name or codes.get(self.pk) != self.code:
            raise ValidationError(
                "ID, название и код статуса должны соответствовать правилам ПР3"
            )


class ProjectQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status__code=Status.Code.COMPLETED)

    def completed(self):
        return self.filter(status__code=Status.Code.COMPLETED)

    def planned(self):
        return self.filter(status__code=Status.Code.PLANNED)

    def in_progress(self):
        return self.filter(status__code=Status.Code.ACTIVE)

    def for_date(self, value):
        return self.filter(deadline=value)

    def overdue(self, today=None):
        return self.active().filter(deadline__lt=today or date.today())

    def with_related(self):
        return self.select_related("developer", "status").prefetch_related(
            "technologies"
        )


def new_slug():
    return "project-" + uuid4().hex


class Project(NamedEntity):
    slug = models.SlugField("Адрес", max_length=80, unique=True, default=new_slug)
    is_completed = models.GeneratedField(
        expression=models.Case(
            models.When(status_id=3, then=models.Value(True)),
            default=models.Value(False),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )
    developer = models.ForeignKey(
        Developer,
        verbose_name="Ответственный",
        on_delete=models.PROTECT,
        related_name="projects",
    )
    status = models.ForeignKey(
        Status,
        verbose_name="Статус",
        on_delete=models.PROTECT,
        related_name="projects",
        default=1,
    )
    technologies = models.ManyToManyField(
        Technology,
        verbose_name="Технологии",
        related_name="projects",
        help_text="Выберите хотя бы одну технологию.",
    )
    deadline = models.DateField(
        "Срок завершения", help_text="Плановая дата завершения проекта."
    )
    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["deadline", "pk"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def get_absolute_url(self):
        return reverse("tracker:slug_detail", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).first()
            if previous and previous.status_id != self.status_id:
                try:
                    validate_transition(previous.status_id, self.status_id)
                except ValueError as error:
                    raise ValidationError({"status": str(error)})

    @transaction.atomic
    def change_status(self, target):
        current = type(self).objects.select_for_update().get(pk=self.pk)
        validate_transition(current.status_id, target)
        current.status_id = target
        current.save(update_fields=["status"])
        self.status_id = target

    def days_remaining(self, today):
        return (self.deadline - today).days
