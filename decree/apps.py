from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DecreeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'decree'
    verbose_name = _("decree_ru")
