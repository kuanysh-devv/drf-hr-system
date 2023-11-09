from django.db import models

from person.models import Person


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

