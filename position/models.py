from django.db import models
from django.utils.translation import gettext_lazy as _
from location.models import Department
from military_rank.models import MilitaryRank


class Position(models.Model):
    positionTitle = models.CharField(max_length=255, verbose_name=_("Position Title"))
    positionTitleKaz = models.CharField(max_length=255, verbose_name=_("Position Title Kaz"), default='Жедел уәкіл')
    order = models.IntegerField(null=True, verbose_name=_("Order"))
    maxRank = models.ForeignKey(MilitaryRank, on_delete=models.CASCADE, default=1, verbose_name=_("Max Rank"))

    def __str__(self):
        return self.positionTitle

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")


class PositionInfo(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name=_("Position"))
    department = models.ForeignKey(Department, models.CASCADE, default=1, verbose_name=_("Department"))
    receivedDate = models.DateField(verbose_name=_("Received Date"))

    def __str__(self):
        return str(self.position) + ' ' + str(self.department.DepartmentName)

    class Meta:
        verbose_name = _("Position Info")
        verbose_name_plural = _("Position Infos")
