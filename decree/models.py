from django.db import models

from person.models import Person


class DecreeList(models.Model):
    decreeType = models.CharField(max_length=255)
    decreeSubType = models.CharField(max_length=255)
    decreeDate = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + self.decreeType


class SpecCheck(models.Model):
    docNumber = models.CharField(max_length=255)
    docDate = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + self.docNumber


class SickLeave(models.Model):
    sickDocNumber = models.CharField(max_length=255)
    sickDocDate = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + self.sickDocNumber


class Investigation(models.Model):
    investigation_decree_type = models.CharField(max_length=255)
    investigation_decree_number = models.CharField(max_length=255)
    investigation_date = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + self.investigation_decree_number
