from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from birth_info.models import BirthInfo
from identity_card_info.models import IdentityCardInfo
from location.models import Department
from photo.models import Photo
from resident_info.models import ResidentInfo
from .models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill
from .serializers import PersonSerializer, GenderSerializer, FamilyStatusSerializer, RelativeSerializer, \
    FamilyCompositionSerializer, ClassCategorySerializer, AutobiographySerializer, RewardSerializer, \
    LanguageSkillSerializer, SportSkillSerializer
from .forms import PersonForm
from birth_info.forms import BirthInfoForm
from identity_card_info.forms import IdentityCardInfoForm
from photo.forms import PhotoForm
from resident_info.forms import ResidentInfoForm
from location.forms import DepartmentForm


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Deserialize the request data using the PersonSerializer
        serializer = PersonSerializer(data=request.data)
        if serializer.is_valid():
            # Create related instances using the request data
            birth_info_data = request.data.get('birthInfoId')
            identity_card_info_data = request.data.get('identityCardInfoId')
            photo_data = request.data.get('photoId')
            resident_info_data = request.data.get('residentInfoId')
            department_data = request.data.get('departmentId')

            birth_info = BirthInfo.objects.create(**birth_info_data)
            identity_card_info = IdentityCardInfo.objects.create(**identity_card_info_data)
            photo = Photo.objects.create(**photo_data)
            resident_info = ResidentInfo.objects.create(**resident_info_data)

            # Link the related instances to the person instance
            person = serializer.save(
                birthInfoId=birth_info,
                identityCardInfoId=identity_card_info,
                photoId=photo,
                residentInfoId=resident_info,
                departmentId=request.data.get('departmentId')
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
