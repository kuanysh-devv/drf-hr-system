from django.apps import AppConfig


class WorkingHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'working_history'

    def ready(self):
        import working_history.signals
