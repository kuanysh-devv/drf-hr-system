from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class WorkingHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'working_history'
    verbose_name = _("working_history_ru")

    def ready(self):
        import working_history.signals
