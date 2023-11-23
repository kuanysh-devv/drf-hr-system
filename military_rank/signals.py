from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver

from military_rank.models import RankInfo


@receiver(post_save, sender=RankInfo)
def rankInfo_post_save(sender, instance, created, **kwargs):
    if created:

        if instance.militaryRank.rankTitle == 'Polkovnik':
            instance.nextPromotionDate = None
            instance.save()
        else:
            next_promotion_days = instance.militaryRank.nextPromotionDateInDays
            new_next_promotion_date = instance.receivedDate + timedelta(days=next_promotion_days)

            instance.nextPromotionDate = new_next_promotion_date
            instance.save()
