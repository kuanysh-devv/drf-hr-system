from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from military_rank.models import RankInfo, MilitaryRank
from person.models import Person, RankArchive


@receiver(post_save, sender=RankInfo)
def rankInfo_post_save(sender, instance, created, **kwargs):
    if created:
        post_save.disconnect(rankInfo_post_save, sender=RankInfo)
        if instance.militaryRank.rankTitle == 'Polkovnik':
            instance.nextPromotionDate = None
            instance.save()

        else:
            received_date_str = instance.receivedDate
            received_date = datetime.strptime(received_date_str, '%Y-%m-%d')
            next_promotion_days = instance.militaryRank.nextPromotionDateInDays
            new_next_promotion_date = received_date + timedelta(days=next_promotion_days)

            instance.nextPromotionDate = new_next_promotion_date
            instance.save()
        post_save.connect(rankInfo_post_save, sender=RankInfo)

    else:
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


@receiver(pre_save, sender=RankInfo)
def create_rank_archive(sender, instance, **kwargs):
    # Check if militaryRank field has changed
    if instance._state.adding or not instance.pk:
        # This is a new instance, not an update
        return

    try:
        # Get the original instance from the database
        original_instance = RankInfo.objects.get(pk=instance.pk)
    except RankInfo.DoesNotExist:
        return

    # Check if militaryRank has changed
    print(original_instance.militaryRank)
    print(instance.militaryRank)
    if original_instance.militaryRank != instance.militaryRank:
        # Create RankArchive instance
        person_instance = Person.objects.get(rankInfo=instance)
        RankArchive.objects.create(
            personId=person_instance,
            militaryRank=original_instance.militaryRank,
            receivedType=original_instance.receivedType,
            decreeNumber=original_instance.decreeNumber,
            startDate=original_instance.receivedDate,
            endDate=timezone.now().date()
        )
