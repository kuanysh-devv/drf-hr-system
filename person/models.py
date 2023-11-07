from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError
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
    role = models.CharField(max_length=255, default='User')

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
    autobiographyText = models.CharField(max_length=2096, null=True)
    autobiographyImage = models.TextField(null=True)
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
