from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from military_rank.models import RankInfo, MilitaryRank
from decree.models import DecreeList, RankUpInfo
from person.models import Person, RankArchive


@receiver(pre_save, sender=RankInfo)
def rankInfo_pre_save(sender, instance, **kwargs):
    if instance._state.adding or not instance.pk:
        if instance.militaryRank.rankTitle == 'Полковник':
            instance.nextPromotionDate = None
        else:
            received_date_string = instance.receivedDate
            next_promotion_days = instance.militaryRank.nextPromotionDateInDays
            received_date = datetime.strptime(received_date_string, '%Y-%m-%d')
            next_promotion_days = int(next_promotion_days)
            new_next_promotion_date = received_date + timedelta(days=next_promotion_days)
            instance.nextPromotionDate = new_next_promotion_date
    else:
        person_instance = Person.objects.get(rankInfo=instance)
        max_rank = person_instance.positionInfo.position.maxRank
        rankUpInfo = None
        non_valid_ranks = MilitaryRank.objects.filter(order__gt=max_rank.order)
        valid_ranks = MilitaryRank.objects.filter(order__lte=max_rank.order)

        try:
            # Get the original instance from the database
            original_instance = RankInfo.objects.get(pk=instance.pk)
        except RankInfo.DoesNotExist:
            return
        print("orig", original_instance)
        print("change", instance)
        # Check if militaryRank has changed
        if original_instance.militaryRank != instance.militaryRank and original_instance.receivedDate != instance.receivedDate:
            # Update the existing RankArchive for the old militaryRank
            person_instance = Person.objects.get(rankInfo=instance)
            try:
                # Try to get the existing RankArchive
                originalRankArchive = RankArchive.objects.get(personId=person_instance,
                                                              militaryRank=original_instance.militaryRank)
            except RankArchive.DoesNotExist:
                raise ObjectDoesNotExist(
                    f"RankArchive for militaryRank '{original_instance.militaryRank}' does not exist.")

            originalRankArchive.endDate = instance.receivedDate
            originalRankArchive.save()

            # Create a new RankArchive for the new militaryRank
            RankArchive.objects.create(
                personId=person_instance,
                militaryRank=instance.militaryRank,
                receivedType=instance.receivedType,
                decreeNumber=instance.decreeNumber,
                startDate=instance.receivedDate,
                endDate=None  # You can update this when the rank changes again
            )

        try:
            rankUpDecree = DecreeList.objects.filter(personId=person_instance, decreeType="Присвоение звания",
                                                    isConfirmed=False).first()
            rankUpInfo = RankUpInfo.objects.get(decreeId=rankUpDecree)
            print(rankUpInfo.receivedType)
            if (rankUpInfo.receivedType == 'Досрочное' or rankUpInfo.receivedType == 'Внеочередное') and instance.militaryRank in non_valid_ranks:

                next_promotion_days = instance.militaryRank.nextPromotionDateInDays
                new_next_promotion_date = instance.receivedDate + timedelta(days=next_promotion_days)
                instance.needPositionUp = False
                instance.nextPromotionDate = new_next_promotion_date
                instance.decreeNumber = rankUpDecree.decreeNumber

            else:
                next_promotion_days = instance.militaryRank.nextPromotionDateInDays
                new_next_promotion_date = instance.receivedDate + timedelta(days=next_promotion_days)
                instance.nextPromotionDate = new_next_promotion_date
                instance.decreeNumber = rankUpDecree.decreeNumber
        except (RankUpInfo.DoesNotExist, DecreeList.DoesNotExist):

            if instance.militaryRank not in valid_ranks:
                original_instance = RankInfo.objects.get(pk=instance.pk)
                instance.militaryRank = original_instance.militaryRank

            next_promotion_days = instance.militaryRank.nextPromotionDateInDays
            new_next_promotion_date = instance.receivedDate + timedelta(days=next_promotion_days)
            instance.needPositionUp = False
            instance.nextPromotionDate = new_next_promotion_date

        except Person.DoesNotExist:
            pass  # Handle Person.DoesNotExist exception as per your requirement

