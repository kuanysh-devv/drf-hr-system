from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PersonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'person'
    verbose_name = _("person_ru")

    def ready(self):
        import person.signals
