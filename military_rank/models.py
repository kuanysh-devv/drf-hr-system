from django.db import models

from person.models import Person


class MilitaryRank(models.Model):
    rankTitle = models.CharField(max_length=255)
    order = models.IntegerField()
    nextPromotionDateInDays = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.rankTitle


class RankInfo(models.Model):
    militaryRank = models.ForeignKey('MilitaryRank', on_delete=models.CASCADE)
    receivedType = models.CharField(max_length=255)
    receivedDate = models.DateField()
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.id)
