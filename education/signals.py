from django.db.models.signals import post_save, post_init, pre_init, pre_save
from django.dispatch import receiver
from django.utils import timezone
from education.models import Attestation


@receiver(pre_save, sender=Attestation)
def attestation_pre_save(sender, instance, **kwargs):
    if instance.attResult == 'Соответствует':
        # If attResult is 'Proshel', set nextAttDateMin to lastAttDate + 3 years
        instance.nextAttDateMin = instance.lastAttDate + timezone.timedelta(days=3 * 365)
        # Set nextAttDateMax to lastAttDate + 3 years 3 months
        instance.nextAttDateMax = instance.lastAttDate + timezone.timedelta(days=(3 * 365) + (6 * 30))
    elif instance.attResult == 'Не соответствует':
         # If attResult is 'Ne proshel', set nextAttDateMin to lastAttDate + 3 months
        instance.nextAttDateMin = instance.lastAttDate + timezone.timedelta(days=3 * 30)
        # Set nextAttDateMax to lastAttDate + 6 months
        instance.nextAttDateMax = instance.lastAttDate + timezone.timedelta(days=6 * 30)

