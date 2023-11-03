from django.contrib.auth.models import AbstractUser
from django.db import models
from birth_info.models import BirthInfo
from identity_card_info.models import IdentityCardInfo
from location.models import Department
from photo.models import Photo
from resident_info.models import ResidentInfo


class Person(models.Model):
    iin = models.CharField(max_length=12)
    pin = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    gender = models.ForeignKey('Gender', on_delete=models.PROTECT)
    nationality = models.CharField(max_length=255)
    familyStatus = models.ForeignKey('FamilyStatus', on_delete=models.PROTECT)
    birthInfoId = models.ForeignKey(BirthInfo, on_delete=models.PROTECT)
    identityCardInfoId = models.ForeignKey(IdentityCardInfo, on_delete=models.PROTECT)
    residentInfoId = models.ForeignKey(ResidentInfo, on_delete=models.PROTECT)
    photoId = models.ForeignKey(Photo, on_delete=models.PROTECT)
    departmentId = models.ForeignKey(Department, on_delete=models.PROTECT)

    def __str__(self):
        return self.iin


class Gender(models.Model):
    genderName = models.CharField(max_length=255)

    def __str__(self):
        return self.genderName


class FamilyStatus(models.Model):
    statusName = models.CharField(max_length=255)

    def __str__(self):
        return self.statusName


class Relative(models.Model):
    relativeName = models.CharField(max_length=255)

    def __str__(self):
        return self.relativeName


class FamilyComposition(models.Model):
    relativeTypeId = models.ForeignKey('Relative', on_delete=models.PROTECT)
    relName = models.CharField(max_length=255)
    relSurname = models.CharField(max_length=255)
    relPatronymic = models.CharField(max_length=255)
    relIin = models.CharField(max_length=12)
    relBirthDate = models.DateField()
    relJobPlace = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.relativeTypeId)


class ClassCategory(models.Model):
    categoryType = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return self.categoryType


class Autobiography(models.Model):
    autobiographyText = models.CharField(max_length=2096)
    autobiographyImage = models.TextField()
    personId = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + 's autobiography'


class Reward(models.Model):
    rewardType = models.CharField(max_length=255)
    rewardDocNumber = models.CharField(max_length=255)
    rewardDate = models.DateField()
    personId = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.rewardType)


class LanguageSkill(models.Model):
    langName = models.CharField(max_length=255)
    skillLvl = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.langName)


class SportSkill(models.Model):
    sportType = models.CharField(max_length=255)
    sportSkillLvl = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.PROTECT)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.sportType)


class CustomUser(AbstractUser):
    person_id = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
