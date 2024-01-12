from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
import logging

from position.models import PositionInfo
from working_history.models import WorkingHistory
from .models import Person

logger = logging.getLogger()


@receiver(pre_delete, sender=Person)
def person_pre_delete(sender, instance, **kwargs):
    try:
        user = get_user_model().objects.get(person_id=instance)
        user.delete()

        instance.positionInfo.delete()
        if instance.rankInfo is not None:
            instance.rankInfo.delete()

    except get_user_model().DoesNotExist:
        pass  # User doesn't exist, no need to delete


@receiver(post_save, sender=Person)
def person_post_save(sender, instance, created, **kwargs):
    if created:
        username = instance.pin
        hashed_password = '123456'

        User = get_user_model()
        user = User.objects.create_user(username=username, password=hashed_password, person_id=instance)
        user.save()
