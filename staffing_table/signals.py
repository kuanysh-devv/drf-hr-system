from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Vacancy, StaffingTable


@receiver(post_save, sender=Vacancy)
def check_max_count(sender, instance, created, **kwargs):
    if created:  # Check if the Vacancy instance is being created (not updated)
        staffing_table = StaffingTable.objects.get(
            staffing_table_position=instance.position,
            staffing_table_department=instance.department
        )

        if staffing_table.current_count + staffing_table.vacancy_list.count() >= staffing_table.max_count:
            raise ValueError("Добавление еще одной вакансии будет превышать максимальное количество")

        staffing_table.vacancy_list.add(instance)
        staffing_table.save()
