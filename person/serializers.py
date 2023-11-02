from rest_framework import serializers

from .models import Person, Relative, FamilyComposition, FamilyStatus, Gender, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = "__all__"


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
