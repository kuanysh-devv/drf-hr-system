from rest_framework import viewsets

from .models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill
from .serializers import PersonSerializer, GenderSerializer, FamilyStatusSerializer, RelativeSerializer, \
    FamilyCompositionSerializer, ClassCategorySerializer, AutobiographySerializer, RewardSerializer, \
    LanguageSkillSerializer, SportSkillSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class GenderViewSet(viewsets.ModelViewSet):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer


class FamilyStatusViewSet(viewsets.ModelViewSet):
    queryset = FamilyStatus.objects.all()
    serializer_class = FamilyStatusSerializer


class RelativeViewSet(viewsets.ModelViewSet):
    queryset = Relative.objects.all()
    serializer_class = RelativeSerializer


class FamilyCompositionViewSet(viewsets.ModelViewSet):
    queryset = FamilyComposition.objects.all()
    serializer_class = FamilyCompositionSerializer


class ClassCategoryViewSet(viewsets.ModelViewSet):
    queryset = ClassCategory.objects.all()
    serializer_class = ClassCategorySerializer


class AutobiographyViewSet(viewsets.ModelViewSet):
    queryset = Autobiography.objects.all()
    serializer_class = AutobiographySerializer


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer


class LanguageSkillViewSet(viewsets.ModelViewSet):
    queryset = LanguageSkill.objects.all()
    serializer_class = LanguageSkillSerializer


class SportSkillViewSet(viewsets.ModelViewSet):
    queryset = SportSkill.objects.all()
    serializer_class = SportSkillSerializer
