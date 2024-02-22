from django.db import models
from django.utils.translation import gettext_lazy as _


class MilitaryRank(models.Model):
    rankTitle = models.CharField(max_length=255, verbose_name=_("Rank Title"))
    order = models.IntegerField(verbose_name=_("Order"))
    pensionAge = models.IntegerField(verbose_name=_("PensionAge"), default=48)
    nextPromotionDateInDays = models.IntegerField(default=1, null=True, verbose_name=_("Next Promotion Date in Days"))

    def __str__(self):
        return self.rankTitle

    class Meta:
        verbose_name = _("Military Rank")
        verbose_name_plural = _("Military Ranks")


class RankInfo(models.Model):
    militaryRank = models.ForeignKey('MilitaryRank', on_delete=models.CASCADE, verbose_name=_("Military Rank"))
    receivedType = models.CharField(max_length=255, verbose_name=_("Received Type"))
    decreeNumber = models.CharField(max_length=1024, default="", null=True, blank=True, verbose_name=_("Decree Number"))
    receivedDate = models.DateField(verbose_name=_("Received Date"))
    nextPromotionDate = models.DateField(null=True, blank=True, verbose_name=_("Next Promotion Date"))
    needPositionUp = models.BooleanField(default=False, verbose_name=_("Need Position Up"))

    def __str__(self):
        try:
            person = self.person_set.get()
            return f"{self.militaryRank.rankTitle} - {person.pin} - {person.surname} {person.firstName} {person.patronymic}"
        except Exception as e:
            return str(e)

    class Meta:
        verbose_name = _("Rank Info")
        verbose_name_plural = _("Rank Infos")

    def create_rank_info_instance_after_minutes(self, minute_count):
        # Calculate the date after the specified number of minutes
        next_promotion_date = datetime.now() + timedelta(minutes=minute_count)

        # Create RankInfo instance
        RankInfo.objects.create(
            militaryRank=self.militaryRank,
            receivedType=self.receivedType,
            decreeNumber=self.decreeNumber,
            receivedDate=datetime.now().date(),
            nextPromotionDate=next_promotion_date.date(),
            needPositionUp=self.needPositionUp
        )