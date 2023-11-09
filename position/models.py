from django.db import models

from location.models import Department
from military_rank.models import MilitaryRank


class Position(models.Model):
    positionTitle = models.CharField(max_length=255)
    order = models.IntegerField(null=True)  # max_length is not needed for IntegerField
    maxRank = models.ForeignKey(MilitaryRank, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.positionTitle


class PositionInfo(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, models.CASCADE, default=1)
    receivedDate = models.DateField()

    def __str__(self):
        return str(self.position)

