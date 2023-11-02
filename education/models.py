from django.db import models

from person.models import Person


class Education(models.Model):
    educationType = models.CharField(max_length=255)
    educationPlace = models.CharField(max_length=255)
    educationDateIn = models.DateField()
    educationDateOut = models.DateField()
    speciality = models.CharField(max_length=255)
    diplomaNumber = models.CharField(max_length=255)
    personId = models.ForeignKey(Person, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + ' ' + self.educationType


class Course(models.Model):
    courseName = models.CharField(max_length=255)
    courseType = models.CharField(max_length=255)
    courseOrg = models.CharField(max_length=255)
    startDate = models.DateField()
    endDate = models.DateField()
    documentType = models.CharField(max_length=255)
    personId = models.ForeignKey(Person, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + ' ' + self.courseName


class Attestation(models.Model):
    attResult = models.CharField(max_length=255)
    lastAttDate = models.DateField()
    nextAttDateMin = models.DateField()
    nextAttDateMax = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + ' ' + self.attResult
