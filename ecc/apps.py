from django.apps import AppConfig
from django.apps import apps
from django.contrib.auth import get_user_model


class EccConfig(AppConfig):
    name = "ecc"
    verbose_name = "ecc"

    def ready(self):
        # Import the Celery app here (rather than at module level) so Django loads it
        # on startup, per Celery's recommended Django integration pattern. `__all__`
        # re-exports it for anything doing `from ecc import celery_app`.
        from .celery import app as celery_app  # noqa: F401
        __all__ = ('celery_app',)  # noqa: F841

        # Activity stream registration
        from actstream import registry

        registry.register(apps.get_model("control.ResponseFile"))
        registry.register(apps.get_model("control.QuestionFile"))
        registry.register(apps.get_model("control.Control"))
        registry.register(apps.get_model("control.Question"))
        registry.register(apps.get_model("control.Questionnaire"))
        registry.register(apps.get_model("control.Theme"))
        registry.register(apps.get_model("auth.Group"))
        registry.register(apps.get_model("user_profiles.UserProfile"))
        registry.register(apps.get_model("faq.FAQItem"))
        registry.register(apps.get_model("admin.LogEntry"))
        registry.register(apps.get_model("sites.Site"))
        registry.register(apps.get_model("django_celery_beat.SolarSchedule"))
        registry.register(apps.get_model("django_celery_beat.IntervalSchedule"))
        registry.register(apps.get_model("django_celery_beat.ClockedSchedule"))
        registry.register(apps.get_model("django_celery_beat.CrontabSchedule"))
        registry.register(apps.get_model("django_celery_beat.PeriodicTasks"))
        registry.register(apps.get_model("django_celery_beat.PeriodicTask"))
        registry.register(apps.get_model("tos.CGUItem"))
        registry.register(apps.get_model("parametres.Parametre"))
        registry.register(apps.get_model("alerte.Alert"))
        registry.register(apps.get_model("control.QuestionnaireFile"))
        registry.register(apps.get_model("user_profiles.Access"))
        registry.register(get_user_model())

        # Signals
        import logs.signals  # noqa
