from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PositionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'position'
    verbose_name = _("position_ru")

    def ready(self):
        import position.signals