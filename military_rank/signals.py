from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from military_rank.models import RankInfo, MilitaryRank
from person.models import Person


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

    else:
        # Code to handle update
        # Disconnect the signal temporarily to avoid recursion
        post_save.disconnect(rankInfo_post_save, sender=RankInfo)

        person_instance = Person.objects.get(rankInfo=instance)
        max_rank = person_instance.positionInfo.position.maxRank
        # next_max_rank = MilitaryRank.objects.get(order=max_rank.order+1)
        non_valid_ranks = MilitaryRank.objects.filter(order__gt=max_rank.order)

        if instance.militaryRank in non_valid_ranks:
            print("Error")
            instance.militaryRank = max_rank
            instance.save()

        else:
            if instance.militaryRank.rankTitle == 'Polkovnik' or instance.militaryRank == max_rank:
                instance.needPositionUp = True
                next_promotion_days = instance.militaryRank.nextPromotionDateInDays
                new_next_promotion_date = instance.receivedDate + timedelta(days=next_promotion_days)
                instance.nextPromotionDate = new_next_promotion_date
                instance.save()
            else:
                next_promotion_days = instance.militaryRank.nextPromotionDateInDays
                new_next_promotion_date = instance.receivedDate + timedelta(days=next_promotion_days)
                instance.needPositionUp = False
                instance.nextPromotionDate = new_next_promotion_date
                instance.save()

        instance.save()

        # Reconnect the signal after saving
        post_save.connect(rankInfo_post_save, sender=RankInfo)
