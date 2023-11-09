from django.db.models.signals import post_save
from django.dispatch import receiver

from location.models import Department
from person.models import Person
from .models import PositionInfo, WorkingHistory


@receiver(post_save, sender=PositionInfo)
def create_working_history(sender, instance, created, **kwargs):

    dep_instance = instance.position.departmentId

    if created:

        WorkingHistory.objects.create(
            positionName=str(instance.position.positionTitle),
            startDate=instance.receivedDate,
            personId=instance.personId,
            department=dep_instance.DepartmentName,
            organizationName="АФМ",
            organizationAddress="Бейбітшілік 10"
            # Add other fields from PositionInfo as needed
        )
