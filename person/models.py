from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
from django.utils.translation import gettext_lazy as _
from military_rank.models import RankInfo, MilitaryRank
from position.models import PositionInfo
from datetime import datetime


class Person(models.Model):
    iin = models.CharField(max_length=12, verbose_name=_("IIN"))
    pin = models.CharField(max_length=255, verbose_name=_("PIN"))
    surname = models.CharField(max_length=255, verbose_name=_("Surname"))
    firstName = models.CharField(max_length=255, verbose_name=_("First Name"))
    patronymic = models.CharField(max_length=255, verbose_name=_("Patronymic"))
    gender = models.ForeignKey('Gender', on_delete=models.CASCADE, verbose_name=_("Gender"))
    nationality = models.CharField(max_length=255, verbose_name=_("Nationality"))
    familyStatus = models.ForeignKey('FamilyStatus', on_delete=models.CASCADE, verbose_name=_("Family Status"))
    positionInfo = models.ForeignKey(PositionInfo, on_delete=models.CASCADE, verbose_name=_("Position Info"))
    rankInfo = models.ForeignKey(RankInfo, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_("Rank Info"))
    isFired = models.BooleanField(default=False, verbose_name=_("isFired"))
    inVacation = models.BooleanField(default=False, verbose_name=_("inVacation"))
    inKomandirovka = models.BooleanField(default=False, verbose_name=_("inKomandirovka"))
    role = models.CharField(max_length=255, default='User', verbose_name=_("Role"))

    def next_rank(self):
        current_order = self.rankInfo.militaryRank.order
        try:
            next_rank = MilitaryRank.objects.get(order=current_order + 1)
            return next_rank
        except MilitaryRank.DoesNotExist:
            return None

    def __str__(self):
        return self.iin

    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")


class Gender(models.Model):
    genderName = models.CharField(max_length=255, verbose_name=_("Gender Name"))

    def __str__(self):
        return self.genderName

    class Meta:
        verbose_name = _("Gender")
        verbose_name_plural = _("Genders")


class FamilyStatus(models.Model):
    statusName = models.CharField(max_length=255, verbose_name=_("Status Name"))

    def __str__(self):
        return self.statusName

    class Meta:
        verbose_name = _("FamilyStatus")
        verbose_name_plural = _("FamilyStatuses")


class Relative(models.Model):
    relativeName = models.CharField(max_length=255, verbose_name=_("Relative Name"))

    def __str__(self):
        return self.relativeName

    class Meta:
        verbose_name = _("Relative")
        verbose_name_plural = _("Relatives")


class FamilyComposition(models.Model):
    relativeType = models.ForeignKey('Relative', on_delete=models.PROTECT, verbose_name=_("Relative Type"))
    relName = models.CharField(max_length=255, verbose_name=_("Relative Name"))
    relSurname = models.CharField(max_length=255, verbose_name=_("Relative Surname"))
    relPatronymic = models.CharField(max_length=255, verbose_name=_("Relative Patronymic"))
    relIin = models.CharField(max_length=12, verbose_name=_("Relative IIN"))
    relBirthDate = models.DateField(verbose_name=_("Relative Birth Date"))
    relJobPlace = models.CharField(max_length=255, verbose_name=_("Relative Job Place"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.relativeType)

    class Meta:
        verbose_name = _("FamilyComposition")
        verbose_name_plural = _("FamilyCompositions")


class ClassCategory(models.Model):
    categoryType = models.CharField(max_length=255, verbose_name=_("Category Type"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return self.categoryType

    class Meta:
        verbose_name = _("ClassCategory")
        verbose_name_plural = _("ClassCategories")


class Autobiography(models.Model):
    autobiographyText = models.CharField(max_length=2096, null=True, verbose_name=_("Autobiography Text"))
    autobiographyImage = models.TextField(null=True, verbose_name=_("Autobiography Image"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + 's autobiography'

    class Meta:
        verbose_name = _("Autobiography")
        verbose_name_plural = _("Autobiographies")


class Reward(models.Model):
    rewardType = models.CharField(max_length=255, verbose_name=_("Reward Type"))
    rewardDocNumber = models.CharField(max_length=255, verbose_name=_("Reward Document Number"))
    rewardDate = models.DateField(verbose_name=_("Reward Date"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + str(self.rewardType)

    class Meta:
        verbose_name = _("Reward")
        verbose_name_plural = _("Rewards")


class LanguageSkill(models.Model):
    langName = models.CharField(max_length=255, verbose_name=_("Language Name"))
    skillLvl = models.CharField(max_length=255, verbose_name=_("Language Skill Level"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + str(self.langName)

    class Meta:
        verbose_name = _("LanguageSkill")
        verbose_name_plural = _("LanguageSkills")


class SportSkill(models.Model):
    sportType = models.CharField(max_length=255, verbose_name=_("Sport Type"))
    sportSkillLvl = models.CharField(max_length=255, verbose_name=_("Sport Skill Level"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId) + ' ' + str(self.sportType)

    class Meta:
        verbose_name = _("SportSkill")
        verbose_name_plural = _("SportSkills")


class CustomUser(AbstractUser):
    person_id = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        try:
            if self.person_id:
                if self.is_superuser and self.is_staff:
                    self.person_id.role = 'Admin'
                    self.person_id.save()
                elif self.is_superuser:
                    self.person_id.role = 'Admin'
                    self.person_id.save()
                elif self.is_staff:
                    self.person_id.role = 'Moderator'
                    self.person_id.save()
                else:
                    # Set a default role for other users if needed
                    self.person_id.role = 'User'
                    self.person_id.save()
        except IntegrityError:
            # Handle the IntegrityError that occurs when a Person instance doesn't exist.
            # You can create a Person instance here if needed.
            pass

        super().save(*args, **kwargs)


class RankArchive(models.Model):
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))
    militaryRank = models.ForeignKey(MilitaryRank, on_delete=models.CASCADE, verbose_name=_("Military Rank"))
    receivedType = models.CharField(max_length=255, verbose_name=_("Received Type"))
    decreeNumber = models.CharField(max_length=1024, default="", null=True, blank=True, verbose_name=_("Decree Number"))
    startDate = models.DateField(verbose_name=_("Start Date"))
    endDate = models.DateField(verbose_name=_("End Date"), null=True, blank=True)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.militaryRank.rankTitle)

    class Meta:
        verbose_name = _("RankArchive")
        verbose_name_plural = _("RankArchives")


class Vacation(models.Model):
    year = models.IntegerField(default=datetime.now().year, verbose_name=_("Vacation year"))
    daysType = models.CharField(default="Обычные", verbose_name=_("Vacation days type"))
    daysCount = models.IntegerField(default=0, verbose_name=_("Vacation days count"))
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1, verbose_name=_("Person"))

    def __str__(self):
        return str(self.personId.iin) + " - " + str(self.daysType) + " " + str(self.daysCount) + "(" + str(
            self.year) + ")"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'daysType', 'personId'], name='unique_vacation')
        ]

        verbose_name = _("Vacation")
        verbose_name_plural = _("Vacations")


class Holidays(models.Model):
    holidayDate = models.DateField(default=None, verbose_name=_("Holiday date"))
    holidayTitle = models.CharField(verbose_name=_("Holiday title"), max_length=255)

    def __str__(self):
        return str(self.holidayTitle) + " - " + str(self.holidayDate)

    class Meta:
        verbose_name = _("Holiday")
        verbose_name_plural = _("Holidays")
