from django.apps import AppConfig


class TrackerConfig(AppConfig):
    name = "tracker"
    verbose_name = "Учет программных проектов"

    def ready(self):
        from . import signals  # noqa: F401
