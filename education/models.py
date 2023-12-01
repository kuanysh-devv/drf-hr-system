from django.db import models
from django.utils.translation import gettext_lazy as _

from person.models import Person


class Education(models.Model):
    educationType = models.CharField(max_length=255, verbose_name=_("Education Type"))
    educationPlace = models.CharField(max_length=255, verbose_name=_("Education Place"))
    educationDateIn = models.DateField(verbose_name=_("Education Start Date"))
    educationDateOut = models.DateField(verbose_name=_("Education End Date"))
    speciality = models.CharField(max_length=255, verbose_name=_("Speciality"))
    diplomaNumber = models.CharField(max_length=255, verbose_name=_("Diploma Number"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + self.educationType

    class Meta:
        verbose_name = _("Education")
        verbose_name_plural = _("Educations")


class Course(models.Model):
    courseName = models.CharField(max_length=255, verbose_name=_("Course Name"))
    courseType = models.CharField(max_length=255, verbose_name=_("Course Type"))
    courseOrg = models.CharField(max_length=255, verbose_name=_("Course Organization"))
    startDate = models.DateField(verbose_name=_("Start Date"))
    endDate = models.DateField(verbose_name=_("End Date"))
    documentType = models.CharField(max_length=255, verbose_name=_("Document Type"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + self.courseName

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")


class Attestation(models.Model):
    attResult = models.CharField(max_length=255, verbose_name=_("Attestation Result"))
    lastAttDate = models.DateField(verbose_name=_("Last Attestation Date"))
    nextAttDateMin = models.DateField(null=True, blank=True, verbose_name=_("Next Attestation Date (Min)"))
    nextAttDateMax = models.DateField(null=True, blank=True, verbose_name=_("Next Attestation Date (Max)"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + self.attResult

    class Meta:
        verbose_name = _("Attestation")
        verbose_name_plural = _("Attestations")


class AcademicDegree(models.Model):
    academicPlace = models.CharField(max_length=255, verbose_name=_("Academic Place"))
    academicDegree = models.CharField(max_length=255, verbose_name=_("Academic Degree"))
    academicDiplomaNumber = models.CharField(max_length=255, verbose_name=_("Academic Diploma Number"))
    academicDiplomaDate = models.DateField(verbose_name=_("Academic Diploma Date"))
    personId = models.ForeignKey(Person, on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + self.academicDegree

    class Meta:
        verbose_name = _("Academic Degree")
        verbose_name_plural = _("Academic Degrees")
