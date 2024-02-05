from django.db import models
from django.utils.translation import gettext_lazy as _
from person.models import Person
from location.models import Department
from position.models import Position
from military_rank.models import MilitaryRank


class DecreeList(models.Model):
    decreeType = models.CharField(max_length=255, verbose_name=_("Decree Type"))
    decreeNumber = models.CharField(max_length=255, verbose_name=_("Decree Number"), null=True, blank=True)
    decreeDate = models.DateField(verbose_name=_("Decree Date"))
    isConfirmed = models.BooleanField(default=False, verbose_name=_("isConfirmed"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))
    minioDocName = models.CharField(max_length=4048, default="None", verbose_name=_("minioDocName"))

    class Meta:
        verbose_name = _("Decree List")
        verbose_name_plural = _("Decree Lists")

    def __str__(self):
        return self.decreeType + ' - ИИН: ' + str(self.personId) + ' - Дата: ' + str(self.decreeDate)


class AppointmentInfo(models.Model):
    appointmentDepartment = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name=_("Appointment Department"))
    appointmentPosition = models.ForeignKey(Position, on_delete=models.CASCADE, verbose_name=_("Appointment Position"))
    appointmentProbation = models.IntegerField(verbose_name=_("Appointment Probation"), null=True, blank=True)
    appointmentBase = models.CharField(max_length=255, verbose_name=_("Appointment Base"))
    appointmentType = models.CharField(max_length=255, default="None", verbose_name=_("Appointment Type"))
    decreeId = models.ForeignKey(DecreeList, on_delete=models.CASCADE, default=1, verbose_name=_("Decree id"))

    class Meta:
        verbose_name = _("AppointmentInfo")
        verbose_name_plural = _("AppointmentInfos")

    def __str__(self):
        return ' Архив ' + self.decreeId.decreeType + ' - ИИН: ' + str(self.decreeId.personId) + ' - от ' + str(
            self.decreeId.decreeDate)


class TransferInfo(models.Model):
    previousDepartment = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_("Previous Department"),
        related_name='previous_transfer_infos'  # Add a unique related_name
    )
    previousPosition = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        verbose_name=_("Previous Position"),
        related_name='previous_transfer_infos'  # Add a unique related_name
    )
    newDepartment = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name=_("New Department"),
        related_name='new_transfer_infos'  # Add a unique related_name
    )
    newPosition = models.ForeignKey(
        Position,
        on_delete=models.CASCADE,
        verbose_name=_("New Position"),
        related_name='new_transfer_infos'  # Add a unique related_name
    )
    transferBase = models.CharField(max_length=255, verbose_name=_("Transfer Base"))
    decreeId = models.ForeignKey(
        DecreeList,
        on_delete=models.CASCADE,
        default=1,
        verbose_name=_("Decree id")
    )

    class Meta:
        verbose_name = _("TransferInfo")
        verbose_name_plural = _("TransferInfos")

    def __str__(self):
        return ' Архив ' + self.decreeId.decreeType + ' - ИИН: ' + str(self.decreeId.personId) + ' - от ' + str(
            self.decreeId.decreeDate)


class RankUpInfo(models.Model):
    previousRank = models.ForeignKey(
        MilitaryRank,
        on_delete=models.CASCADE,
        verbose_name=_("Previous Rank"),
        related_name='previous_rank_up_infos'  # Add a unique related_name
    )
    newRank = models.ForeignKey(
        MilitaryRank,
        on_delete=models.CASCADE,
        verbose_name=_("New Rank"),
        related_name='new_rank_up_infos'  # Add a unique related_name
    )
    receivedType = models.CharField(max_length=255, verbose_name=_("Received Type"))
    decreeId = models.ForeignKey(
        'DecreeList',
        on_delete=models.CASCADE,
        default=1,
        verbose_name=_("Decree id")
    )

    class Meta:
        verbose_name = _("RankUpInfo")
        verbose_name_plural = _("RankUpInfos")

    def __str__(self):
        return ' Архив ' + self.decreeId.decreeType + ' - ИИН: ' + str(self.decreeId.personId) + ' - от ' + str(
            self.decreeId.decreeDate)


class SpecCheck(models.Model):
    docNumber = models.CharField(max_length=255, verbose_name=_("Document Number"))
    docDate = models.DateField(verbose_name=_("Document Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Spec Check")
        verbose_name_plural = _("Spec Checks")

    def __str__(self):
        return str(self.personId) + ' ' + self.docNumber


class SickLeave(models.Model):
    sickDocNumber = models.CharField(max_length=255, verbose_name=_("Sick Document Number"))
    sickDocDate = models.DateField(verbose_name=_("Sick Document Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Sick Leave")
        verbose_name_plural = _("Sick Leaves")

    def __str__(self):
        return str(self.personId) + ' ' + self.sickDocNumber


class Investigation(models.Model):
    investigation_decree_type = models.CharField(max_length=255, verbose_name=_("Investigation Decree Type"))
    investigation_decree_number = models.CharField(max_length=255, verbose_name=_("Investigation Decree Number"))
    investigation_date = models.DateField(verbose_name=_("Investigation Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    class Meta:
        verbose_name = _("Investigation")
        verbose_name_plural = _("Investigations")

    def __str__(self):
        return str(self.personId) + ' ' + self.investigation_decree_number
