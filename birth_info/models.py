from django.db import models


class BirthInfo(models.Model):
    birth_date = models.DateField()
    country = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    district = models.CharField(max_length=255)

    def __str__(self):
        return str(self.id)
