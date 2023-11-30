from django.db import models


class MilitaryRank(models.Model):
    rankTitle = models.CharField(max_length=255)
    order = models.IntegerField()
    nextPromotionDateInDays = models.IntegerField(default=1, null=True)

    def __str__(self):
        return self.rankTitle


class RankInfo(models.Model):
    militaryRank = models.ForeignKey('MilitaryRank', on_delete=models.CASCADE)
    receivedType = models.CharField(max_length=255)
    decreeNumber = models.CharField(max_length=1024, default="", null=True, blank=True)
    receivedDate = models.DateField()
    nextPromotionDate = models.DateField(null=True, blank=True)
    needPositionUp = models.BooleanField(default=False)

    def __str__(self):
        return str(self.militaryRank.rankTitle) + ' ' + str(self.id)
