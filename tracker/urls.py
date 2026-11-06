from django.urls import path
from . import views

app_name = "tracker"
urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("projects/", views.project_list, name="projects"),
    path("projects/export/", views.project_export, name="export"),
    path("projects/new/", views.project_edit, name="create"),
    path("projects/<int:pk>/", views.project_detail, name="detail"),
    path("projects/<int:pk>/edit/", views.project_edit, name="edit"),
    path("projects/<int:pk>/delete/", views.project_delete, name="delete"),
    path("projects/by-slug/<slug:slug>/", views.project_detail, name="slug_detail"),
    path("developers/", views.developers, name="developers"),
    path("developers/<int:pk>/", views.developer_detail, name="developer"),
    path("technologies/", views.technologies, name="technologies"),
    path("statistics/", views.statistics, name="statistics"),
    path("available/", views.available, name="available"),
    path(
        "developers/new/",
        views.reference_edit,
        {"kind": "developer"},
        name="developer_create",
    ),
    path(
        "developers/<int:pk>/edit/",
        views.reference_edit,
        {"kind": "developer"},
        name="developer_edit",
    ),
    path(
        "developers/<int:pk>/delete/",
        views.reference_delete,
        {"kind": "developer"},
        name="developer_delete",
    ),
    path(
        "technologies/new/",
        views.reference_edit,
        {"kind": "technology"},
        name="technology_create",
    ),
    path(
        "technologies/<int:pk>/edit/",
        views.reference_edit,
        {"kind": "technology"},
        name="technology_edit",
    ),
    path(
        "technologies/<int:pk>/delete/",
        views.reference_delete,
        {"kind": "technology"},
        name="technology_delete",
    ),
]
