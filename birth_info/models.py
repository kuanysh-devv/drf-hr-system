from django.db import models

from person.models import Person


class BirthInfo(models.Model):
    birth_date = models.DateField()
    country = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.id)
