from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BirthInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'birth_info'
    verbose_name = _("birth_info_ru")
