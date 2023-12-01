from django.db import models
from django.utils.translation import gettext as _

from person.models import Person


class BirthInfo(models.Model):
    birth_date = models.DateField(verbose_name=_("Birth Date"))
    country = models.CharField(max_length=255, verbose_name=_("Country"))
    region = models.CharField(max_length=255, verbose_name=_("Region"))
    city = models.CharField(max_length=255, verbose_name=_("City"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Birth_Info")
        verbose_name_plural = _("Birth Infos")

    def __str__(self):
        return str(self.id)
