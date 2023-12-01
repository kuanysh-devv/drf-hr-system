from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MilitaryRankConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'military_rank'
    verbose_name = _("military_rank_ru")

    def ready(self):
        import military_rank.signals
