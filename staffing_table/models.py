from django.db import models
from django.utils.translation import gettext_lazy as _
from location.models import Department
from position.models import Position


class Vacancy(models.Model):
    position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name=_("Position"))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("Department"))
    available_date = models.DateField(verbose_name=_("Available Date"))

    def __str__(self):
        return (str("Вакансия - ") + str(self.department.DepartmentName) +
                " - " + str(self.position.positionTitle) + " - " + str(self.available_date))

    class Meta:
        verbose_name = _("Vacancy")
        verbose_name_plural = _("Vacancies")


class StaffingTable(models.Model):
    staffing_table_position = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name=_("Position"))
    staffing_table_department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("Department"))
    vacancy_list = models.ManyToManyField('Vacancy', verbose_name=_("Vacancy List"), blank=True)
    current_count = models.IntegerField(default=0, verbose_name=_("Current Count"))
    max_count = models.IntegerField(verbose_name=_("Max Count"))

    def __str__(self):
        if self.vacancy_list.exists():
            first_vacancy = self.vacancy_list.first()
            return str("Штатное расписание - ") + str(first_vacancy.department.DepartmentName) + " - " + str(
                first_vacancy.position.positionTitle)
        else:
            return str("Штатное расписание - ") + str(self.staffing_table_department.DepartmentName) + " - " + str(
                self.staffing_table_position.positionTitle)

    class Meta:
        verbose_name = _("Staffing Table")
        verbose_name_plural = _("Staffing Tables")
