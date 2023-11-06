from django.db import models

from person.models import Person


class ResidentInfo(models.Model):
    resCountry = models.CharField(max_length=255)
    resRegion = models.CharField(max_length=255)
    resCity = models.CharField(max_length=255)
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.id)
