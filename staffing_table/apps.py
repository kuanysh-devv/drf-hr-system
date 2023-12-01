from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StaffingTableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staffing_table'
    verbose_name = _("staffing_table_ru")

    def ready(self):
        import staffing_table.signals
