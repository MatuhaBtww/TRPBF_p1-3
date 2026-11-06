from django.contrib import admin
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
    list_display = ["id", "name"]
    search_fields = ["name"]
    ordering = ["name"]
    inlines = [ProjectInline]


@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


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
    search_fields = ["name", "developer__name", "technologies__name"]
    list_filter = ["status", "developer", "technologies", "deadline"]
    ordering = ["deadline", "pk"]
    list_per_page = 10
    list_select_related = ["developer", "status"]
    filter_horizontal = ["technologies"]
    readonly_fields = ["slug", "is_completed"]


admin.site.site_header = "Система учета программных проектов"
admin.site.site_title = "Учет проектов"
admin.site.index_title = "Управление данными"
