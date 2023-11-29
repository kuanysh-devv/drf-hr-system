from datetime import timedelta

from django.db.models.signals import post_save, post_init
from django.dispatch import receiver

from education.models import Attestation
from military_rank.models import RankInfo


@receiver(post_save, sender=Attestation)
def attestation_post_save(sender, instance, created, **kwargs):
    if created:
        if instance.attResult == 'Соответствует':
            # If attResult is 'Proshel', set nextAttDateMin to lastAttDate + 3 years
            instance.nextAttDateMin = instance.lastAttDate + timedelta(days=3 * 365)
            # Set nextAttDateMax to lastAttDate + 3 years 3 months
            instance.nextAttDateMax = instance.lastAttDate + timedelta(days=(3 * 365) + (3 * 30))
        elif instance.attResult == 'Не соответствует':
            # If attResult is 'Ne proshel', set nextAttDateMin to lastAttDate + 3 months
            instance.nextAttDateMin = instance.lastAttDate + timedelta(days=3 * 30)
            # Set nextAttDateMax to lastAttDate + 6 months
            instance.nextAttDateMax = instance.lastAttDate + timedelta(days=6 * 30)

        # Save the updated instance
        instance.save()


@receiver(post_init, sender=Attestation)
def attestation_post_init(sender, instance, **kwargs):
    if instance.attResult == 'Соответствует':
        # If attResult is 'Proshel', set nextAttDateMin to lastAttDate + 3 years
        instance.nextAttDateMin = instance.lastAttDate + timedelta(days=3 * 365)
        # Set nextAttDateMax to lastAttDate + 3 years 3 months
        instance.nextAttDateMax = instance.lastAttDate + timedelta(days=(3 * 365) + (3 * 30))
    elif instance.attResult == 'Не соответствует':
        # If attResult is 'Ne proshel', set nextAttDateMin to lastAttDate + 3 months
        instance.nextAttDateMin = instance.lastAttDate + timedelta(days=3 * 30)
        # Set nextAttDateMax to lastAttDate + 6 months
        instance.nextAttDateMax = instance.lastAttDate + timedelta(days=6 * 30)

