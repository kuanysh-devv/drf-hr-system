from django.db import models


class ResidentInfo(models.Model):
    resCountry = models.CharField(max_length=255)
    resRegion = models.CharField(max_length=255)
    resCity = models.CharField(max_length=255)

    def __str__(self):
        return str(self.id)
