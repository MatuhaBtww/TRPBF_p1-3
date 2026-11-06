from django.contrib import admin, messages
from django.db import transaction
from django.db.models import Count, Q
from django.core.exceptions import ValidationError
from .models import Developer, Technology, Status, Project
from .forms import ProjectForm


class ProjectInline(admin.TabularInline):
    model = Project
    fields = ["name", "deadline", "status"]
    readonly_fields = fields
    extra = 0
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "active_projects"]
    list_display_links = ["id", "name"]
    search_fields = ["name"]
    ordering = ["name"]
    readonly_fields = ["id"]
    inlines = [ProjectInline]

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .annotate(
                active_count=Count(
                    "projects", filter=~Q(projects__status__code=Status.Code.COMPLETED)
                )
            )
        )

    @admin.display(description="Незавершенных проектов", ordering="active_count")
    def active_projects(self, obj):
        return obj.active_count


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]
    readonly_fields = ["id"]

    def get_deleted_objects(self, objs, request):
        deleted, counts, permissions, protected = super().get_deleted_objects(
            objs, request
        )
        ids = {obj.pk for obj in objs}
        for project in (
            Project.objects.filter(technologies__in=ids)
            .distinct()
            .prefetch_related("technologies")
        ):
            if not any(t.pk not in ids for t in project.technologies.all()):
                protected.append(
                    f"Проект «{project.name}»: нельзя удалить все его технологии"
                )
        return deleted, counts, permissions, protected


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "code"]
    readonly_fields = ["id", "name", "code"]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    form = ProjectForm
    list_display = ["id", "name", "developer", "status", "deadline", "is_completed"]
    list_display_links = ["id", "name"]
    list_editable = ["deadline"]
    search_fields = ["name", "developer__name", "technologies__name"]
    list_filter = ["status", "developer", "technologies", "deadline"]
    ordering = ["deadline", "pk"]
    list_per_page = 10
    list_select_related = ["developer", "status"]
    readonly_fields = ["id", "slug", "is_completed"]
    autocomplete_fields = ["developer"]
    date_hierarchy = "deadline"
    actions = ["start_projects", "plan_projects", "complete_projects"]

    def transition(self, request, queryset, target):
        changed = 0
        skipped = 0
        for obj in queryset.order_by("pk"):
            try:
                with transaction.atomic():
                    obj.change_status(target)
                changed += 1
            except (ValueError, ValidationError):
                skipped += 1
        self.message_user(
            request,
            f"Изменено: {changed}. Пропущено из-за правил перехода: {skipped}.",
            messages.WARNING if skipped else messages.SUCCESS,
        )

    @admin.action(
        description="Перевести выбранные проекты в работу", permissions=["change"]
    )
    def start_projects(self, request, queryset):
        self.transition(request, queryset, 2)

    @admin.action(
        description="Вернуть выбранные проекты в план", permissions=["change"]
    )
    def plan_projects(self, request, queryset):
        self.transition(request, queryset, 1)

    @admin.action(description="Завершить выбранные проекты", permissions=["change"])
    def complete_projects(self, request, queryset):
        self.transition(request, queryset, 3)


admin.site.site_header = "Система учета программных проектов"
admin.site.site_title = "Учет проектов"
admin.site.index_title = "Управление данными"
