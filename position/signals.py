from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError

from position.models import PositionInfo
from staffing_table.models import StaffingTable


@receiver(pre_save, sender=PositionInfo)
def position_info_pre_save(sender, instance, **kwargs):
    # Check if the instance is being created (not updated)
    if instance._state.adding:
        # Get the associated department and position
        department = instance.department
        position = instance.position

        try:
            # Retrieve the staffing table entry for the department and position
            staffing_entry = StaffingTable.objects.get(department=department, position=position)

            # Check if adding a new position exceeds the max_count
            if staffing_entry.current_count + 1 > staffing_entry.max_count:
                raise ValidationError('Adding this position would exceed the maximum count for the department.')

            # Increment the current_count for the position in the staffing table
            staffing_entry.current_count += 1
            staffing_entry.save()

        except StaffingTable.DoesNotExist:
            # Handle the case where there is no staffing entry for the department and position
            raise ValidationError('No staffing entry found for the department and position.')

    # If the instance is being updated, the logic can be adjusted accordingly
    # ...


@receiver(pre_delete, sender=PositionInfo)
def position_info_pre_delete(sender, instance, **kwargs):
    # Check if the instance being deleted is associated with a department and position
    if instance.department and instance.position:
        try:
            # Retrieve the staffing table entry for the department and position
            staffing_entry = StaffingTable.objects.get(department=instance.department, position=instance.position)

            # Ensure that the current_count is greater than zero before decrementing
            if staffing_entry.current_count > 0:
                staffing_entry.current_count -= 1
                staffing_entry.save()

        except StaffingTable.DoesNotExist:
            # Handle the case where there is no staffing entry for the department and position
            pass
