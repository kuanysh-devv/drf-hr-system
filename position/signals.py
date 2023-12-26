from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from person.models import Person
from position.models import PositionInfo
from staffing_table.models import StaffingTable
from working_history.models import WorkingHistory


@receiver(pre_save, sender=PositionInfo)
def pre_save_position_info(sender, instance, **kwargs):
    # Check if the 'position' or 'department' fields are being updated
    if instance.pk is not None:
        original_instance = PositionInfo.objects.get(pk=instance.pk)
        if original_instance.position != instance.position or original_instance.department != instance.department:
            # Get the person associated with the PositionInfo
            person = Person.objects.get(positionInfo=instance)

            # -1 to old job place in staffing table
            try:
                # Retrieve the staffing table entry for the department and position
                staffing_entry = StaffingTable.objects.get(department=original_instance.department,
                                                           position=original_instance.position)

                if staffing_entry.current_count > 0:
                    staffing_entry.current_count -= 1
                    staffing_entry.save()

            except StaffingTable.DoesNotExist:
                # Handle the case where there is no staffing entry for the department and position
                raise ValidationError('Не было найдено штатного расписания с указанными должностью и департаментом')

            # +1 to new job place in staffing table
            try:
                # Retrieve the staffing table entry for the department and position
                staffing_entry = StaffingTable.objects.get(department=instance.department, position=instance.position)

                if staffing_entry.current_count + 1 > staffing_entry.max_count:
                    raise ValidationError('Добавление этой должности будет превышать максимальное количество для '
                                          'департамента')

                # Increment the current_count for the position in the staffing table
                staffing_entry.current_count += 1
                staffing_entry.save()

            except StaffingTable.DoesNotExist:
                # Handle the case where there is no staffing entry for the department and position
                raise ValidationError('Не было найдено штатного расписания с указанными должностью и департаментом')

            workingHistoryList = WorkingHistory.objects.filter(personId=person)
            print(workingHistoryList)
            last_working_history = workingHistoryList.order_by('id').last()
            print(last_working_history)
            if last_working_history:
                last_working_history.endDate = instance.receivedDate
                last_working_history.save()

            # Create a new WorkingHistory object with the updated information
            new_working_history = WorkingHistory(
                positionName=instance.position.positionTitle,
                startDate=instance.receivedDate,
                endDate=None,
                department=instance.department.DepartmentName,
                organizationName='АФМ',
                organizationAddress='Бейбітшілік 10',
                personId=person,
            )
            new_working_history.save()


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
                raise ValidationError('Добавление этой должности будет превышать максимальное количество для '
                                      'департамента')

            # Increment the current_count for the position in the staffing table
            staffing_entry.current_count += 1
            staffing_entry.save()

        except StaffingTable.DoesNotExist:
            # Handle the case where there is no staffing entry for the department and position
            raise ValidationError('Не было найдено штатного расписания с указанными должностью и департаментом')

    # If the instance is being updated, the logic can be adjusted accordingly
    # ...


@receiver(pre_delete, sender=PositionInfo)
def position_info_pre_delete(sender, instance, **kwargs):
    # Check if the instance being deleted is associated with a department and position
    if instance.department and instance.position:
        try:
            # Retrieve the staffing table entry for the department and position
            staffing_entry = StaffingTable.objects.get(department=instance.department, position=instance.position)
            print(staffing_entry)
            # Ensure that the current_count is greater than zero before decrementing
            if staffing_entry.current_count > 0:
                staffing_entry.current_count -= 1
                staffing_entry.save()

        except StaffingTable.DoesNotExist:
            # Handle the case where there is no staffing entry for the department and position
            pass
