from django.db import models

from person.models import Person


class IdentityCardInfo(models.Model):
    identityCardNumber = models.CharField(max_length=9)
    issuedBy = models.CharField(max_length=255)
    dateOfIssue = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.id)
