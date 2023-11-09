from rest_framework import serializers
from location.models import Department
from location.serializers import DepartmentSerializer
from .models import Person, Relative, FamilyComposition, FamilyStatus, Gender, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill

from rest_framework import serializers
from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    familyStatus = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = "__all__"

    @staticmethod
    def get_familyStatus(obj):
        familyStatus = obj.familyStatus
        if familyStatus:
            return FamilyStatusSerializer(familyStatus).data
        return None

    @staticmethod
    def get_department(obj):
        department = obj.department
        if department:
            return DepartmentSerializer(department).data
        return None

    @staticmethod
    def get_gender(obj):
        gender = obj.gender
        if gender:
            return GenderSerializer(gender).data
        return None

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
