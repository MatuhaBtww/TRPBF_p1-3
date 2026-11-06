from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from django.db.models import QuerySet
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from .models import Project, Technology


@receiver(m2m_changed, sender=Project.technologies.through)
def require_technology(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in ("pre_remove", "pre_clear"):
        return
    if reverse:
        projects = instance.projects.all()
        if pk_set is not None:
            projects = projects.filter(pk__in=pk_set)
        for project in projects:
            if project.technologies.count() == 1:
                raise ValidationError("Проект должен иметь хотя бы одну технологию")
    elif (
        action == "pre_clear"
        or not instance.technologies.exclude(pk__in=pk_set).exists()
    ):
        raise ValidationError("Проект должен иметь хотя бы одну технологию")


@receiver(pre_delete, sender=Technology)
def protect_last_technology(sender, instance, **kwargs):
    origin = kwargs.get("origin")
    removed = (
        set(origin.values_list("pk", flat=True))
        if isinstance(origin, QuerySet) and origin.model is Technology
        else {instance.pk}
    )
    if any(
        not ({t.pk for t in p.technologies.all()} - removed)
        for p in instance.projects.prefetch_related("technologies")
    ):
        raise ProtectedError(
            "Нельзя удалить единственную технологию проекта",
            list(instance.projects.all()),
        )
