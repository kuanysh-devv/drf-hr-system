from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class IdentityCardInfoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'identity_card_info'
    verbose_name = _("identity_card_info_ru")
