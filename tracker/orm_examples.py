from datetime import date
from django.db.models import Q, Count, Min, Max, F
from .models import Project, Developer


def examples():
    first = Project.objects.order_by("pk").first()
    return {
        "all": list(Project.objects.all()),
        "filter": list(Project.objects.filter(status_id=1)),
        "and": list(
            Project.objects.filter(status_id=2, deadline__lte=date(2026, 12, 31))
        ),
        "related": list(Project.objects.filter(developer__name__icontains="Анна")),
        "exclude": list(Project.objects.exclude(status_id=3)),
        "search": list(Project.objects.filter(name__icontains="система")),
        "or": list(
            Project.objects.filter(
                Q(name__icontains="система") | Q(developer__name__icontains="Иван")
            )
        ),
        "not": list(Project.objects.filter(~Q(status_id=3))),
        "sort": list(Project.objects.order_by("-deadline", "pk")),
        "slice": list(Project.objects.order_by("pk")[0:5]),
        "first": Project.objects.order_by("pk").first(),
        "get": Project.objects.get(pk=first.pk) if first else None,
        "select_related": list(Project.objects.select_related("developer", "status")),
        "prefetch": list(Project.objects.prefetch_related("technologies")),
        "values": list(Project.objects.values("name", "developer__name")),
        "aggregate": Project.objects.aggregate(
            total=Count("pk"), first=Min("deadline"), last=Max("deadline")
        ),
        "annotate": list(
            Developer.objects.annotate(total=Count("projects")).values("name", "total")
        ),
        "F": list(
            Project.objects.annotate(owner_name=F("developer__name")).values(
                "name", "owner_name"
            )
        ),
        "active": list(Project.objects.active()),
        "completed": list(Project.objects.completed()),
        "overdue": list(Project.objects.overdue(date(2026, 11, 6))),
    }
