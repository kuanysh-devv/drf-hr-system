from django.db import models
from django.utils.translation import gettext_lazy as _
from location.models import Department
from position.models import Position


class StaffingTable(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name=_("Position"))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("Department"))
    current_count = models.IntegerField(default=0, verbose_name=_("Current Count"))
    max_count = models.IntegerField(verbose_name=_("Max Count"))

    def __str__(self):
        return str("Штатное расписание - ") + str(self.department.DepartmentName) + " - " + str(self.position.positionTitle)

    class Meta:
        verbose_name = _("Staffing Table")
        verbose_name_plural = _("Staffing Tables")
