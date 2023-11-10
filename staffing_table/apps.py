from django.apps import AppConfig


class StaffingTableConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staffing_table'

    def ready(self):
        import staffing_table.signals
