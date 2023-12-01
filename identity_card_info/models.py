from django.db import models
from django.utils.translation import gettext_lazy as _

from person.models import Person


class IdentityCardInfo(models.Model):
    identityCardNumber = models.CharField(max_length=9, verbose_name=_("Identity Card Number"))
    issuedBy = models.CharField(max_length=255, verbose_name=_("Issued By"))
    dateOfIssue = models.DateField(verbose_name=_("Date of Issue"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + self.identityCardNumber

    class Meta:
        verbose_name = _("Identity Card Info")
        verbose_name_plural = _("Identity Card Infos")
