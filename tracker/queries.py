from datetime import date
from django.db.models import Count, Q, F, Min, Max
from .models import Project, Developer, Technology, Status

SORT_FIELDS = {
    "deadline": ("deadline", "pk"),
    "-deadline": ("-deadline", "pk"),
    "name": ("name", "pk"),
    "-name": ("-name", "pk"),
    "developer": ("developer__name", "deadline", "pk"),
}


def filtered_projects(params):
    projects = Project.objects.all()
    query = params.get("q")
    if query:
        projects = projects.filter(
            Q(name__icontains=query)
            | Q(developer__name__icontains=query)
            | Q(technologies__name__icontains=query)
        ).distinct()
    methods = {"1": "planned", "2": "in_progress", "3": "completed"}
    if params.get("status"):
        projects = getattr(projects, methods[params["status"]])()
    if params.get("date"):
        projects = projects.for_date(params["date"])
    if params.get("developer"):
        projects = projects.filter(developer=params["developer"])
    if params.get("technology"):
        projects = projects.filter(technologies=params["technology"])
    return projects.order_by(*SORT_FIELDS[params.get("sort") or "deadline"])


def project_rows(projects):
    return projects.annotate(
        developer_name=F("developer__name"), status_name=F("status__name")
    ).values("id", "name", "slug", "deadline", "developer_name", "status_name")


def developer_totals():
    return Developer.objects.annotate(
        total=Count("projects"),
        active_total=Count(
            "projects", filter=~Q(projects__status__code=Status.Code.COMPLETED)
        ),
    ).order_by("name", "pk")


def technology_totals():
    return Technology.objects.annotate(total=Count("projects")).order_by(
        "-total", "name", "pk"
    )


def summary():
    return Project.objects.aggregate(
        total=Count("pk"),
        planned=Count("pk", filter=Q(status__code=Status.Code.PLANNED)),
        active=Count("pk", filter=Q(status__code=Status.Code.ACTIVE)),
        completed=Count("pk", filter=Q(status__code=Status.Code.COMPLETED)),
        overdue=Count(
            "pk",
            filter=~Q(status__code=Status.Code.COMPLETED)
            & Q(deadline__lt=date.today()),
        ),
        first_deadline=Min("deadline"),
        last_deadline=Max("deadline"),
    )


def status_totals():
    return Status.objects.annotate(total=Count("projects")).order_by("pk")


def available_developers(on_date):
    busy = Project.objects.active().filter(deadline__lte=on_date).values("developer_id")
    return Developer.objects.exclude(pk__in=busy)
