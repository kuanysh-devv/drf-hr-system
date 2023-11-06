from django.contrib.auth.models import AbstractUser
from django.db import models
from location.models import Department


class Person(models.Model):
    iin = models.CharField(max_length=12)
    pin = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    firstName = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    gender = models.ForeignKey('Gender', on_delete=models.CASCADE)
    nationality = models.CharField(max_length=255)
    familyStatus = models.ForeignKey('FamilyStatus', on_delete=models.CASCADE)
    departmentId = models.ForeignKey(Department, on_delete=models.CASCADE)

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
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.relativeTypeId)


class ClassCategory(models.Model):
    categoryType = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return self.categoryType


class Autobiography(models.Model):
    autobiographyText = models.CharField(max_length=2096)
    autobiographyImage = models.TextField()
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + 's autobiography'


class Reward(models.Model):
    rewardType = models.CharField(max_length=255)
    rewardDocNumber = models.CharField(max_length=255)
    rewardDate = models.DateField()
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.rewardType)


class LanguageSkill(models.Model):
    langName = models.CharField(max_length=255)
    skillLvl = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.langName)


class SportSkill(models.Model):
    sportType = models.CharField(max_length=255)
    sportSkillLvl = models.CharField(max_length=255)
    personId = models.ForeignKey('Person', on_delete=models.CASCADE, default=1)

    def __str__(self):
        return str(self.personId) + ' ' + str(self.sportType)


class CustomUser(AbstractUser):
    person_id = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
