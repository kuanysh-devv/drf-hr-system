from django.db import models


class Photo(models.Model):
    photoBinary = models.TextField()

    def __str__(self):
        return str(self.id)
