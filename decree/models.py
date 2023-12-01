from django.db import models
from django.utils.translation import gettext_lazy as _
from person.models import Person


class DecreeList(models.Model):
    decreeType = models.CharField(max_length=255, verbose_name=_("Decree Type"))
    decreeSubType = models.CharField(max_length=255, verbose_name=_("Decree SubType"))
    decreeDate = models.DateField(verbose_name=_("Decree Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Decree List")
        verbose_name_plural = _("Decree Lists")


class SpecCheck(models.Model):
    docNumber = models.CharField(max_length=255, verbose_name=_("Document Number"))
    docDate = models.DateField(verbose_name=_("Document Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Spec Check")
        verbose_name_plural = _("Spec Checks")

    def __str__(self):
        return str(self.personId) + ' ' + self.docNumber


class SickLeave(models.Model):
    sickDocNumber = models.CharField(max_length=255, verbose_name=_("Sick Document Number"))
    sickDocDate = models.DateField(verbose_name=_("Sick Document Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Sick Leave")
        verbose_name_plural = _("Sick Leaves")

    def __str__(self):
        return str(self.personId) + ' ' + self.sickDocNumber


class Investigation(models.Model):
    investigation_decree_type = models.CharField(max_length=255, verbose_name=_("Investigation Decree Type"))
    investigation_decree_number = models.CharField(max_length=255, verbose_name=_("Investigation Decree Number"))
    investigation_date = models.DateField(verbose_name=_("Investigation Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Investigation")
        verbose_name_plural = _("Investigations")

    def __str__(self):
        return str(self.personId) + ' ' + self.investigation_decree_number
