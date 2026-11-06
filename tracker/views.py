from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError, transaction
from django.db.models import Q, Count
from django.http import HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, Developer, Technology, Status
from .forms import ProjectForm


def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def project_list(request):
    projects = Project.objects.with_related()
    query = request.GET.get("q", "").strip()
    if query:
        projects = projects.filter(
            Q(name__icontains=query)
            | Q(developer__name__icontains=query)
            | Q(technologies__name__icontains=query)
        ).distinct()
    status = request.GET.get("status", "")
    if status:
        if status not in ("1", "2", "3"):
            return HttpResponseBadRequest("Некорректный статус")
        projects = projects.filter(status_id=int(status))
    sort = request.GET.get("sort", "deadline")
    if sort not in ("deadline", "-deadline", "name", "-name"):
        return HttpResponseBadRequest("Некорректная сортировка")
    projects = projects.order_by(sort, "pk")
    page = Paginator(projects, 5).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(
        request,
        "projects.html",
        {
            "projects": page,
            "page": page,
            "params": params.urlencode(),
            "statuses": Status.objects.all(),
            "sort": sort,
            "selected_status": status,
        },
    )


def project_detail(request, pk=None, slug=None):
    lookup = {"slug": slug} if slug else {"pk": pk}
    p = get_object_or_404(Project.objects.with_related(), **lookup)
    return render(
        request, "detail.html", {"p": p, "technologies": p.technologies.all()}
    )


def developers(request):
    return render(
        request,
        "references.html",
        {
            "title": "Разработчики",
            "items": Developer.objects.annotate(total=Count("projects")),
        },
    )


def developer_detail(request, pk):
    p = get_object_or_404(Developer, pk=pk)
    return render(
        request,
        "developer.html",
        {"developer": p, "projects": p.projects.with_related()},
    )


def technologies(request):
    return render(
        request,
        "references.html",
        {"title": "Технологии", "items": Technology.objects.all()},
    )


def statistics(request):
    stats = {
        s.name: s.total
        for s in Status.objects.annotate(total=Count("projects")).order_by("pk")
    }
    stats["Просрочено"] = Project.objects.overdue().count()
    stats["Всего проектов"] = Project.objects.count()
    return render(request, "statistics.html", {"stats": stats})


def available(request):
    value = request.GET.get("date", date.today().isoformat())
    try:
        selected = date.fromisoformat(value)
    except ValueError:
        return render(
            request, "available.html", {"error": "Некорректная дата"}, status=400
        )
    busy = (
        Project.objects.active().filter(deadline__lte=selected).values("developer_id")
    )
    return render(
        request,
        "available.html",
        {"items": Developer.objects.exclude(pk__in=busy), "date": value},
    )


@staff_member_required
def project_edit(request, pk=None):
    p = get_object_or_404(Project, pk=pk) if pk else None
    form = ProjectForm(request.POST or None, instance=p)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                obj = form.save()
            return redirect("tracker:detail", pk=obj.pk)
        except (ValidationError, DatabaseError):
            form.add_error(
                None,
                "Не удалось сохранить проект. Проверьте данные и повторите попытку.",
            )
    return render(request, "form.html", {"form": form})


def not_found(request, exception):
    return render(request, "404.html", status=404)
