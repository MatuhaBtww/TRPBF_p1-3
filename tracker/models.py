from datetime import date
from uuid import uuid4
from django.urls import reverse
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.db import models, transaction
from rules import STATUS_NAMES, validate_name, validate_transition


class NamedEntity(models.Model):
    name = models.CharField("Название", max_length=200)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True
        ordering = ["name", "pk"]

    def clean(self):
        super().clean()
        try:
            self.name = validate_name(self.name)
        except ValueError as error:
            raise ValidationError({"name": str(error)})

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
        if (
            STATUS_NAMES.get(self.pk) != self.name
            or {1: "planned", 2: "active", 3: "completed"}.get(self.pk) != self.code
        ):
            raise ValidationError(
                "ID и название статуса должны соответствовать правилам ПР3"
            )


class ProjectQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status_id=3)

    def completed(self):
        return self.filter(status_id=3)

    def planned(self):
        return self.filter(status_id=1)

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

    def get_absolute_url(self):
        return reverse("tracker:slug_detail", kwargs={"slug": self.slug})

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
        Technology, verbose_name="Технологии", related_name="projects"
    )
    deadline = models.DateField("Срок завершения")
    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["deadline", "pk"]
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"

    def clean(self):
        super().clean()
        if self.pk:
            previous = type(self).objects.filter(pk=self.pk).first()
            if previous and previous.status_id != self.status_id:
                try:
                    validate_transition(previous.status_id, self.status_id)
                except ValueError as error:
                    raise ValidationError({"status": str(error)})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @transaction.atomic
    def change_status(self, target):
        current = type(self).objects.select_for_update().get(pk=self.pk)
        validate_transition(current.status_id, target)
        current.status_id = target
        current.save(update_fields=["status"])
        self.status_id = target

    def days_remaining(self, today):
        return (self.deadline - today).days
