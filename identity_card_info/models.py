from django.db import models


class IdentityCardInfo(models.Model):
    identityCardNumber = models.CharField(max_length=9)
    issuedBy = models.CharField(max_length=255)
    dateOfIssue = models.DateField()

    def __str__(self):
        return str(self.id)
