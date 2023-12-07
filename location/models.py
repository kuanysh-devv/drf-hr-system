from django.db import models
from django.utils.translation import gettext_lazy as _


class Location(models.Model):
    LocationName = models.CharField(max_length=255, verbose_name=_("Location Name"))

    def __str__(self):
        return self.LocationName

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class Department(models.Model):
    DepartmentName = models.CharField(max_length=255, verbose_name=_("Department Name"))
    DepartmentNameKaz = models.CharField(max_length=255, verbose_name=_("Department Name Kaz"), default='На казахском')
    Location = models.ForeignKey('Location', on_delete=models.CASCADE, verbose_name=_("Location"))

    def __str__(self):
        return str(self.DepartmentName)

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

