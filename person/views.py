from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from birth_info.models import BirthInfo
from birth_info.serializers import BirthInfoSerializer
from education.serializers import CourseSerializer, AcademicDegreeSerializer, EducationSerializer
from identity_card_info.models import IdentityCardInfo
from identity_card_info.serializers import IdentityCardInfoSerializer
from location.models import Department
from photo.models import Photo
from photo.serializers import PhotoSerializer
from position.serializers import WorkingHistorySerializer, PositionInfoSerializer
from resident_info.models import ResidentInfo
from resident_info.serializers import ResidentInfoSerializer
from .models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill
from .serializers import PersonSerializer, GenderSerializer, FamilyStatusSerializer, RelativeSerializer, \
    FamilyCompositionSerializer, ClassCategorySerializer, AutobiographySerializer, RewardSerializer, \
    LanguageSkillSerializer, SportSkillSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        # Deserialize the request data using the PersonSerializer
        serializer = PersonSerializer(data=request.data.get('Person'))
        if serializer.is_valid():
            # Create the Person instance
            person_instance_data = request.data.get('Person')

            department_data = person_instance_data.get('departmentId')

            # Link the related instances to the person instance
            person = serializer.save(
                departmentId=department_data
            )

            # Handle the related objects

            birth_info_data = request.data.get('BirthInfo')
            birth_info_serializer = BirthInfoSerializer(data=birth_info_data)
            if birth_info_serializer.is_valid():
                birth_info_serializer.save(personId=person)
                print("BirthInfo done")
            else:
                return Response(birth_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            identity_card_info_data = request.data.get('IdentityCardInfo')
            identity_card_info_serializer = IdentityCardInfoSerializer(data=identity_card_info_data)
            if identity_card_info_serializer.is_valid():
                identity_card_info_serializer.save(personId=person)
                print("IdentityCardInfo done")
            else:
                return Response(identity_card_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            photo_data = request.data.get('Photo')
            photo_serializer = PhotoSerializer(data=photo_data)
            if photo_serializer.is_valid():
                photo_serializer.save(personId=person)
                print("Photo done")
            else:
                return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            resident_info_data = request.data.get('ResidentInfo')
            resident_info_serializer = ResidentInfoSerializer(data=resident_info_data)
            if resident_info_serializer.is_valid():
                resident_info_serializer.save(personId=person)
                print("ResidentInfo done")
            else:
                return Response(resident_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # PositionInfo
            position_info_data = request.data.get('PositionInfo')
            position_info_serializer = PositionInfoSerializer(data=position_info_data)
            if position_info_serializer.is_valid():
                position_info_serializer.save(personId=person)
                print("positioninfo done")
            else:
                return Response(position_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # FamilyComposition
            family_composition_data = request.data.get('FamilyComposition')
            relatives_data = family_composition_data.get('relatives')
            for relative_data in relatives_data:
                relative_serializer = FamilyCompositionSerializer(data=relative_data)
                if relative_serializer.is_valid():
                    relative_serializer.save(personId=person)
                    print("family_composition done")
                else:
                    return Response(relative_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Education
            education_data = request.data.get('Education')
            educations_data = education_data.get('educations')
            for education_data in educations_data:
                education_serializer = EducationSerializer(data=education_data)
                if education_serializer.is_valid():
                    education_serializer.save(personId=person)
                    print("education done")
                else:
                    return Response(education_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # LanguageSkill
            language_skill_data = request.data.get('LanguageSkill')
            language_skills_data = language_skill_data.get('languageSkills')
            for language_skill_data in language_skills_data:
                language_skill_serializer = LanguageSkillSerializer(data=language_skill_data)
                if language_skill_serializer.is_valid():
                    language_skill_serializer.save(personId=person)
                    print("language_skill done")
                else:
                    return Response(language_skill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # AcademicDegree
            academic_degree_data = request.data.get('AcademicDegree')
            academic_degrees_data = academic_degree_data.get('academicDegrees')
            for academic_degree_data in academic_degrees_data:
                academic_degree_serializer = AcademicDegreeSerializer(data=academic_degree_data)
                if academic_degree_serializer.is_valid():
                    academic_degree_serializer.save(personId=person)
                    print("academic_degree done")
                else:
                    return Response(academic_degree_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Course
            course_data = request.data.get('Course')
            courses_data = course_data.get('courses')
            for course_data in courses_data:
                course_serializer = CourseSerializer(data=course_data)
                if course_serializer.is_valid():
                    course_serializer.save(personId=person)
                    print("course done")
                else:
                    return Response(course_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # SportSkill
            sport_skill_data = request.data.get('SportSkill')
            sport_skills_data = sport_skill_data.get('sportSkills')
            for sport_skill_data in sport_skills_data:
                sport_skill_serializer = SportSkillSerializer(data=sport_skill_data)
                if sport_skill_serializer.is_valid():
                    sport_skill_serializer.save(personId=person)
                    print("sport_skill done")
                else:
                    return Response(sport_skill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # WorkingHistory
            working_history_data = request.data.get('WorkingHistory')
            working_histories_data = working_history_data.get('workingHistories')
            for working_history_data in working_histories_data:
                working_history_serializer = WorkingHistorySerializer(data=working_history_data)
                if working_history_serializer.is_valid():
                    working_history_serializer.save(personId=person)
                    print("working_history done")
                else:
                    return Response(working_history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    permission_classes = (IsAuthenticated,)


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
