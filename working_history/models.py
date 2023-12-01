from django.db import models
from django.utils.translation import gettext_lazy as _
from person.models import Person


class WorkingHistory(models.Model):
    positionName = models.CharField(max_length=255, verbose_name=_("Position Name"))
    startDate = models.DateField(verbose_name=_("Start Date"))
    endDate = models.DateField(null=True, blank=True, verbose_name=_("End Date"))
    department = models.CharField(max_length=255, null=True, verbose_name=_("Department"))
    organizationName = models.CharField(max_length=255, verbose_name=_("Organization Name"))
    organizationAddress = models.CharField(max_length=492, null=True, verbose_name=_("Organization Address"))
    isPravoOhranka = models.BooleanField(default=False, verbose_name=_("Is Pravo Ohranka"))
    HaveCoefficient = models.BooleanField(default=False, verbose_name=_("Have Coefficient"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.positionName)

    class Meta:
        verbose_name = _("Working History")
        verbose_name_plural = _("Working Histories")
