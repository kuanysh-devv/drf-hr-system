from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ResidentInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'resident_info'
    verbose_name = _("resident_info_ru")
