from django.db import models


class Location(models.Model):
    LocationName = models.CharField(max_length=255)

    def __str__(self):
        return self.LocationName


class Department(models.Model):
    DepartmentName = models.CharField(max_length=255)
    Location = models.ForeignKey('Location', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)
