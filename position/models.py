from django.db import models

from location.models import Department
from military_rank.models import MilitaryRank
from person.models import Person


class Position(models.Model):
    positionTitle = models.CharField(max_length=255)
    order = models.IntegerField(null=True)  # max_length is not needed for IntegerField
    departmentId = models.ForeignKey(Department, models.CASCADE, default=0)
    maxRank = models.ForeignKey(MilitaryRank, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.positionTitle


class PositionInfo(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    receivedDate = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.position)


class WorkingHistory(models.Model):
    positionName = models.CharField(max_length=255)
    startDate = models.DateField()
    endDate = models.DateField(null=True)
    department = models.CharField(max_length=255, null=True)
    organizationName = models.CharField(max_length=255)
    organizationAddress = models.CharField(max_length=492, null=True)
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.positionName)
