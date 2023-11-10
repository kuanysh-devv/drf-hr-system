from django.db import models

from location.models import Department
from position.models import Position


class StaffingTable(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    current_count = models.IntegerField(default=0)
    max_count = models.IntegerField()

    def __str__(self):
        return str(self.id)
