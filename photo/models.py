from django.db import models

from person.models import Person


class Photo(models.Model):
    photoBinary = models.TextField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.id)
