import csv
from datetime import date
from functools import wraps
import logging
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import DatabaseError, transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Project, Developer, Technology
from .forms import (
    ProjectForm,
    ProjectFilterForm,
    DateForm,
    DeveloperForm,
    TechnologyForm,
)
from . import queries

logger = logging.getLogger(__name__)


def staff_permission(permission):
    def decorator(view):
        @login_required
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_staff or not request.user.has_perm(permission):
                raise PermissionDenied
            return view(request, *args, **kwargs)

        return wrapped

    return decorator


def home(request):
    return render(
        request,
        "home.html",
        {
            "summary": queries.summary(),
            "upcoming": Project.objects.active()
            .with_related()
            .order_by("deadline", "pk")[:3],
        },
    )


def about(request):
    return render(request, "about.html")


def project_list(request):
    form = ProjectFilterForm(request.GET or None)
    valid = form.is_valid() if form.is_bound else True
    params = form.cleaned_data if form.is_bound and valid else {}
    projects = queries.filtered_projects(params) if valid else Project.objects.none()
    table = request.GET.get("view") == "table"
    projects = queries.project_rows(projects) if table else projects.with_related()
    page = Paginator(projects, 5).get_page(request.GET.get("page"))
    links = request.GET.copy()
    links.pop("page", None)
    switch = links.copy()
    switch.pop("view", None)
    return render(
        request,
        "projects.html",
        {
            "form": form,
            "projects": page,
            "page": page,
            "params": links.urlencode(),
            "switch_params": switch.urlencode(),
            "table": table,
        },
        status=200 if valid else 400,
    )


def project_export(request):
    form = ProjectFilterForm(request.GET or None)
    if form.is_bound and not form.is_valid():
        return project_list(request)
    projects = queries.filtered_projects(form.cleaned_data if form.is_bound else {})
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="projects.csv"'
    response.write("﻿")
    writer = csv.writer(response, delimiter=";")
    writer.writerow(["ID", "Проект", "Разработчик", "Статус", "Срок"])
    for row in queries.project_rows(projects):
        values = [
            row["id"],
            row["name"],
            row["developer_name"],
            row["status_name"],
            row["deadline"],
        ]
        writer.writerow(
            [
                (
                    "'" + v
                    if isinstance(v, str) and v.startswith(("=", "+", "-", "@"))
                    else v
                )
                for v in values
            ]
        )
    return response


def project_detail(request, pk=None, slug=None):
    p = get_object_or_404(
        Project.objects.with_related(), **({"slug": slug} if slug else {"pk": pk})
    )
    return render(
        request,
        "detail.html",
        {
            "p": p,
            "technologies": p.technologies.all(),
            "remaining": p.days_remaining(date.today()),
        },
    )


def developers(request):
    return render(
        request,
        "references.html",
        {
            "title": "Разработчики",
            "kind": "developer",
            "items": queries.developer_totals(),
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
        {
            "title": "Технологии",
            "kind": "technology",
            "items": queries.technology_totals(),
        },
    )


def statistics(request):
    result = queries.summary()
    stats = {s.name: s.total for s in queries.status_totals()}
    stats["Просрочено"] = result["overdue"]
    stats["Всего проектов"] = result["total"]
    return render(
        request,
        "statistics.html",
        {
            "stats": stats,
            "summary": result,
            "developers": queries.developer_totals(),
            "technologies": queries.technology_totals(),
        },
    )


def available(request):
    data = request.GET if "date" in request.GET else {"date": date.today().isoformat()}
    form = DateForm(data)
    valid = form.is_valid()
    items = (
        queries.available_developers(form.cleaned_data["date"])
        if valid
        else Developer.objects.none()
    )
    return render(
        request,
        "available.html",
        {"form": form, "items": items},
        status=200 if valid else 400,
    )


@login_required
def project_edit(request, pk=None):
    permission = "tracker.change_project" if pk else "tracker.add_project"
    if not request.user.is_staff or not request.user.has_perm(permission):
        raise PermissionDenied
    p = get_object_or_404(Project, pk=pk) if pk else None
    form = ProjectForm(request.POST if request.method == "POST" else None, instance=p)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                obj = form.save()
            messages.success(request, "Проект сохранен.")
            return redirect(obj)
        except (ValidationError, DatabaseError):
            logger.exception("Project save failed")
            form.add_error(
                None,
                "Не удалось сохранить проект. Проверьте данные и повторите попытку.",
            )
    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": "Изменить проект" if p else "Добавить проект",
            "cancel_url": p.get_absolute_url() if p else reverse("tracker:projects"),
        },
    )


@staff_permission("tracker.delete_project")
def project_delete(request, pk):
    obj = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Проект удален.")
        return redirect("tracker:projects")
    return render(
        request,
        "confirm_delete.html",
        {"object": obj, "cancel_url": obj.get_absolute_url()},
    )


@login_required
def reference_edit(request, kind, pk=None):
    model, form_class = (
        (Developer, DeveloperForm)
        if kind == "developer"
        else (Technology, TechnologyForm)
    )
    permission = f'tracker.{"change" if pk else "add"}_{kind}'
    if not request.user.is_staff or not request.user.has_perm(permission):
        raise PermissionDenied
    obj = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST if request.method == "POST" else None, instance=obj)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                form.save()
            messages.success(request, "Запись справочника сохранена.")
            return redirect(
                "tracker:developers" if kind == "developer" else "tracker:technologies"
            )
        except (ValidationError, DatabaseError):
            form.add_error(
                None,
                "Не удалось сохранить запись. Проверьте название и повторите попытку.",
            )
    return render(
        request,
        "form.html",
        {
            "form": form,
            "title": ("Изменить" if pk else "Добавить")
            + (" разработчика" if kind == "developer" else " технологию"),
            "cancel_url": reverse(
                "tracker:developers" if kind == "developer" else "tracker:technologies"
            ),
        },
    )


@login_required
def reference_delete(request, kind, pk):
    model = Developer if kind == "developer" else Technology
    if not request.user.is_staff or not request.user.has_perm(f"tracker.delete_{kind}"):
        raise PermissionDenied
    obj = get_object_or_404(model, pk=pk)
    cancel = reverse(
        "tracker:developers" if kind == "developer" else "tracker:technologies"
    )
    error = None
    if request.method == "POST":
        try:
            with transaction.atomic():
                obj.delete()
            messages.success(request, "Запись удалена.")
            return redirect(cancel)
        except (ProtectedError, ValidationError):
            error = "Запись используется проектами. Сначала измените связанные проекты; у каждого должна остаться хотя бы одна технология."
    return render(
        request,
        "confirm_delete.html",
        {"object": obj, "cancel_url": cancel, "error": error},
    )


def not_found(request, exception):
    return render(request, "404.html", status=404)


def forbidden(request, exception):
    return render(request, "403.html", status=403)
