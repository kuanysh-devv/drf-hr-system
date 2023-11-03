from rest_framework import serializers

from birth_info.models import BirthInfo
from birth_info.serializers import BirthInfoSerializer
from identity_card_info.models import IdentityCardInfo
from identity_card_info.serializers import IdentityCardInfoSerializer
from location.models import Department
from photo.models import Photo
from photo.serializers import PhotoSerializer
from resident_info.models import ResidentInfo
from resident_info.serializers import ResidentInfoSerializer
from .models import Person, Relative, FamilyComposition, FamilyStatus, Gender, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill

from rest_framework import serializers
from .models import Person, BirthInfo, IdentityCardInfo, Photo, ResidentInfo


class PersonSerializer(serializers.ModelSerializer):
    # Nested serializers for related models
    birthInfoId = BirthInfoSerializer()
    identityCardInfoId = IdentityCardInfoSerializer()
    photoId = PhotoSerializer()
    residentInfoId = ResidentInfoSerializer()

    # Department field is changed to accept just the department_id (pk)
    departmentId = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=True)

    class Meta:
        model = Person
        fields = "__all__"

    def create(self, validated_data):
        department_id = validated_data.pop('departmentId')  # Remove department_id from validated_data
        department = Department.objects.get(pk=department_id)  # Retrieve the Department instance

        # Create the Person instance with the retrieved Department
        person = Person.objects.create(departmentId=department, **validated_data)

        return person


class RelativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relative
        fields = "__all__"


class FamilyCompositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyComposition
        fields = "__all__"


class FamilyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyStatus
        fields = "__all__"


class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = "__all__"


class ClassCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassCategory
        fields = "__all__"


class AutobiographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Autobiography
        fields = "__all__"


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = "__all__"


class LanguageSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageSkill
        fields = "__all__"


class SportSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SportSkill
        fields = "__all__"
