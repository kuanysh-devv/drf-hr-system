from django.db import models
from django.utils.translation import gettext_lazy as _
from person.models import Person


class ResidentInfo(models.Model):
    resCountry = models.CharField(max_length=255, verbose_name=_("Residence Country"))
    resRegion = models.CharField(max_length=255, verbose_name=_("Residence Region"))
    resCity = models.CharField(max_length=255, verbose_name=_("Residence City"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = _("Resident Info")
        verbose_name_plural = _("Resident Infos")
