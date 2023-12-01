from django.db import models
from django.utils.translation import gettext_lazy as _
from person.models import Person


class Photo(models.Model):
    photoBinary = models.TextField(verbose_name=_("Photo Binary"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId)

    class Meta:
        verbose_name = _("Photo")
        verbose_name_plural = _("Photos")
