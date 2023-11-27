from rest_framework import serializers
from location.models import Department
from location.serializers import DepartmentSerializer
from military_rank.models import RankInfo
from military_rank.serializers import RankInfoSerializer
from photo.models import Photo
from photo.serializers import PhotoSerializer
from position.models import PositionInfo
from position.serializers import PositionInfoSerializer
from .models import Person, Relative, FamilyComposition, FamilyStatus, Gender, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill

from rest_framework import serializers
from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    gender = serializers.SerializerMethodField()
    familyStatus = serializers.SerializerMethodField()
    positionInfo = serializers.SerializerMethodField()
    rankInfo = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = "__all__"

    @staticmethod
    def get_photo(obj):
        try:
            photo = Photo.objects.get(personId=obj)
        except Photo.DoesNotExist:
            return None
        if photo:
            return PhotoSerializer(photo).data
        return None

    @staticmethod
    def get_positionInfo(obj):
        positionInfo = obj.positionInfo
        if positionInfo:
            return PositionInfoSerializer(positionInfo).data
        return None

    @staticmethod
    def get_rankInfo(obj):
        rankInfo = obj.rankInfo
        if rankInfo:
            return RankInfoSerializer(rankInfo).data
        return None

    @staticmethod
    def get_familyStatus(obj):
        familyStatus = obj.familyStatus
        if familyStatus:
            return FamilyStatusSerializer(familyStatus).data
        return None

    @staticmethod
    def get_gender(obj):
        gender = obj.gender
        if gender:
            return GenderSerializer(gender).data
        return None


class RelativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relative
        fields = "__all__"


class FamilyCompositionSerializer(serializers.ModelSerializer):
    relativeType = serializers.SerializerMethodField()

    class Meta:
        model = FamilyComposition
        fields = "__all__"

    @staticmethod
    def get_relativeType(obj):
        relativeType = obj.relativeType
        if relativeType:
            return RelativeSerializer(relativeType).data
        return None


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
