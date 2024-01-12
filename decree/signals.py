# signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from .models import DecreeList


@receiver(pre_save, sender=DecreeList)
def generate_decree_number(sender, instance, **kwargs):
    if not instance.decreeNumber:
        last_id = DecreeList.objects.order_by('-id').first().id if DecreeList.objects.exists() else 0
        prefix = "K" if instance.decreeType == "Перемещение" or instance.decreeType == "Присвоение звания" else ""
        instance.decreeNumber = f"{prefix}{last_id + 1}"

