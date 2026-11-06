from .models import Project


def project_summary(request):
    return {"active_project_count": Project.objects.active().count()}
