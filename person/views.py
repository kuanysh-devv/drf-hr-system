from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill
from .serializers import PersonSerializer, GenderSerializer, FamilyStatusSerializer, RelativeSerializer, \
    FamilyCompositionSerializer, ClassCategorySerializer, AutobiographySerializer, RewardSerializer, \
    LanguageSkillSerializer, SportSkillSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated,)


class GenderViewSet(viewsets.ModelViewSet):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer
    permission_classes = (IsAuthenticated,)


class FamilyStatusViewSet(viewsets.ModelViewSet):
    queryset = FamilyStatus.objects.all()
    serializer_class = FamilyStatusSerializer
    permission_classes = (IsAuthenticated,)


class RelativeViewSet(viewsets.ModelViewSet):
    queryset = Relative.objects.all()
    serializer_class = RelativeSerializer
    permission_classes = (IsAuthenticated, )


class FamilyCompositionViewSet(viewsets.ModelViewSet):
    queryset = FamilyComposition.objects.all()
    serializer_class = FamilyCompositionSerializer
    permission_classes = (IsAuthenticated,)


class ClassCategoryViewSet(viewsets.ModelViewSet):
    queryset = ClassCategory.objects.all()
    serializer_class = ClassCategorySerializer
    permission_classes = (IsAuthenticated,)


class AutobiographyViewSet(viewsets.ModelViewSet):
    queryset = Autobiography.objects.all()
    serializer_class = AutobiographySerializer
    permission_classes = (IsAuthenticated,)


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = (IsAuthenticated,)


class LanguageSkillViewSet(viewsets.ModelViewSet):
    queryset = LanguageSkill.objects.all()
    serializer_class = LanguageSkillSerializer
    permission_classes = (IsAuthenticated,)


class SportSkillViewSet(viewsets.ModelViewSet):
    queryset = SportSkill.objects.all()
    serializer_class = SportSkillSerializer
    permission_classes = (IsAuthenticated,)
