import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from birth_info.models import BirthInfo
from birth_info.serializers import BirthInfoSerializer
from decree.models import SpecCheck, SickLeave, Investigation, DecreeList
from decree.serializers import SpecCheckSerializer, SickLeaveSerializer, InvestigationSerializer, DecreeListSerializer
from education.models import Education, AcademicDegree, Course, Attestation
from education.serializers import CourseSerializer, AcademicDegreeSerializer, EducationSerializer, AttestationSerializer
from identity_card_info.models import IdentityCardInfo
from identity_card_info.serializers import IdentityCardInfoSerializer
from location.models import Department
from military_rank.models import RankInfo, MilitaryRank
from military_rank.serializers import RankInfoSerializer
from photo.models import Photo
from photo.serializers import PhotoSerializer
from position.models import PositionInfo, Position

from position.serializers import PositionInfoSerializer
from resident_info.models import ResidentInfo
from resident_info.serializers import ResidentInfoSerializer
from working_history.models import WorkingHistory
from working_history.serializers import WorkingHistorySerializer
from .models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill, CustomUser
from .serializers import PersonSerializer, GenderSerializer, FamilyStatusSerializer, RelativeSerializer, \
    FamilyCompositionSerializer, ClassCategorySerializer, AutobiographySerializer, RewardSerializer, \
    LanguageSkillSerializer, SportSkillSerializer


@csrf_exempt
def departments_persons(request, *args, **kwargs):
    try:

        department_id = request.GET.get('department_id', None)

        department = Department.objects.get(pk=department_id)
        persons = Person.objects.filter(positionInfo__department=department)

        serializer = PersonSerializer(persons, many=True)

        return JsonResponse({'persons': serializer.data})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['PATCH'])
    def update_family_status(self, request, pk=None):
        try:
            person = self.get_object()
            family_status_name = request.data.get('statusName')

            # Check if family_status_id is provided
            if family_status_name is None:
                return Response({'error': 'family_status is required'}, status=status.HTTP_400_BAD_REQUEST)

            family_status = FamilyStatus.objects.get(statusName=family_status_name)

            # Update the person's familyStatus
            person.familyStatus = family_status
            person.save()

            serializer = PersonSerializer(person)
            return Response(serializer.data)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        except FamilyStatus.DoesNotExist:
            return Response({'error': 'Family status not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def update_gender(self, request, pk=None):
        """
        Update the gender of a person.
        """
        try:
            person = self.get_object()
            gender_name = request.data.get('genderName')

            # Validate and get the Gender instance
            try:
                gender_instance = Gender.objects.get(genderName=gender_name)
            except Gender.DoesNotExist:
                return Response({'error': 'Gender not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update the gender field
            person.gender = gender_instance
            person.save()

            # Serialize the updated person
            serializer = PersonSerializer(person)
            return Response(serializer.data)

        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, *args, **kwargs):
        person = self.get_object()

        # Serialize the person data
        person_serializer = PersonSerializer(person)

        birth_info_object = BirthInfo.objects.get(personId=person.id)
        birth_info_serializer = BirthInfoSerializer(birth_info_object)

        identity_card_info_object = IdentityCardInfo.objects.get(personId=person.id)
        identity_card_info_serializer = IdentityCardInfoSerializer(identity_card_info_object)

        resident_info_object = ResidentInfo.objects.get(personId=person.id)
        resident_info_serializer = ResidentInfoSerializer(resident_info_object)

        family_composition_objects = FamilyComposition.objects.filter(personId=person.id)
        family_composition_data = FamilyCompositionSerializer(family_composition_objects, many=True).data

        education_objects = Education.objects.filter(personId=person.id)
        education_data = EducationSerializer(education_objects, many=True).data

        language_skill_objects = LanguageSkill.objects.filter(personId=person.id)
        language_skill_data = LanguageSkillSerializer(language_skill_objects, many=True).data

        academic_degree_objects = AcademicDegree.objects.filter(personId=person.id)
        academic_degree_data = AcademicDegreeSerializer(academic_degree_objects, many=True).data

        course_objects = Course.objects.filter(personId=person.id)
        course_data = CourseSerializer(course_objects, many=True).data

        sport_skill_objects = SportSkill.objects.filter(personId=person.id)
        sport_skill_data = SportSkillSerializer(sport_skill_objects, many=True).data

        working_history_objects = WorkingHistory.objects.filter(personId=person.id)
        working_history_data = WorkingHistorySerializer(working_history_objects, many=True).data

        spec_check_objects = SpecCheck.objects.filter(personId=person.id)
        spec_check_data = SpecCheckSerializer(spec_check_objects, many=True).data

        attestation_objects = Attestation.objects.filter(personId=person.id)
        attestation_data = AttestationSerializer(attestation_objects, many=True).data

        class_categories_objects = ClassCategory.objects.filter(personId=person.id)
        class_categories_data = ClassCategorySerializer(class_categories_objects, many=True).data

        autobiography_objects = Autobiography.objects.filter(personId=person.id)
        autobiography_data = AutobiographySerializer(autobiography_objects, many=True).data

        rewards_objects = Reward.objects.filter(personId=person.id)
        rewards_data = RewardSerializer(rewards_objects, many=True).data

        sick_leaves_objects = SickLeave.objects.filter(personId=person.id)
        sick_leaves_data = SickLeaveSerializer(sick_leaves_objects, many=True).data

        investigation_objects = Investigation.objects.filter(personId=person.id)
        investigation_data = InvestigationSerializer(investigation_objects, many=True).data

        decree_list_objects = DecreeList.objects.filter(personId=person.id)
        decree_list_data = DecreeListSerializer(decree_list_objects, many=True).data

        # Create a dictionary with the serialized data
        data = {
            'Person': person_serializer.data,
            'BirthInfo': birth_info_serializer.data,
            'IdentityCardInfo': identity_card_info_serializer.data,
            'ResidentInfo': resident_info_serializer.data,
            'FamilyComposition': {'relatives': family_composition_data},
            'Education': {'educations': education_data},
            'LanguageSkill': {'languageSkills': language_skill_data},
            'AcademicDegree': {'academicDegrees': academic_degree_data},
            'Course': {'courses': course_data},
            'SportSkill': {'sportSkills': sport_skill_data},
            'WorkingHistory': {'workingHistories': working_history_data},
            'SpecCheckInfo': {'specChecks': spec_check_data},
            'AttestationInfo': {'attestations': attestation_data},
            'ClassCategoriesInfo': {'classCategories': class_categories_data},
            'AutobiographyInfo': {'autobiographies': autobiography_data},
            'RewardsInfo': {'rewards': rewards_data},
            'SickLeavesInfo': {'sickLeaves': sick_leaves_data},
            'InvestigationsInfo': {'investigations': investigation_data},
            'DecreeListInfo': {'decrees': decree_list_data}
            # Add more data for other related objects
        }

        return Response(data)

    def create(self, request, *args, **kwargs):
        # Deserialize the request data using the PersonSerializer
        posSerializer = PositionInfoSerializer(data=request.data.get('PositionInfo'))
        rankSerializer = RankInfoSerializer(data=request.data.get('RankInfo'))
        if posSerializer.is_valid() and rankSerializer.is_valid():
            # Create the Person instance
            positionInfoData = request.data.get('PositionInfo')
            positionName = positionInfoData.get('position')
            positionInstance = Position.objects.get(positionTitle=positionName)

            departmentName = positionInfoData.get('department')
            departmentInstance = Department.objects.get(DepartmentName=departmentName)

            rankInfoData = request.data.get('RankInfo')
            rankName = rankInfoData.get('militaryRank')
            rankInstance = MilitaryRank.objects.get(rankTitle=rankName)

            posinfo = posSerializer.save(position=positionInstance, department=departmentInstance)
            rankInfo = rankSerializer.save(militaryRank=rankInstance)

            person_data = request.data.get('Person')
            genderName = person_data.get('gender')
            genderInstance = Gender.objects.get(genderName=genderName)
            familyStatusName = person_data.get('familyStatus')
            familyStatusInstance = FamilyStatus.objects.get(statusName=familyStatusName)

            person_serializer = PersonSerializer(data=person_data)

            if person_serializer.is_valid():
                person = person_serializer.save(positionInfo=posinfo, rankInfo=rankInfo, gender=genderInstance,
                                                familyStatus=familyStatusInstance)
            else:
                return Response(person_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

            # Photo
            try:
                # Check if 'Photo' key is present in the request data
                if 'Photo' in request.data:
                    photo_data = request.data.get('Photo')

                    # Check if 'photoBinary' key is present and it's not an empty string
                    if 'photoBinary' in photo_data and photo_data['photoBinary']:
                        photo_serializer = PhotoSerializer(data=photo_data)

                        if photo_serializer.is_valid():
                            photo_serializer.save(personId=person)
                            print("Photo done")
                        else:
                            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'photoBinary' key is not present or it's an empty string
                        print("No photoBinary provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'Photo' key is not present
                    print("Photo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # ResidentInfo
            resident_info_data = request.data.get('ResidentInfo')
            resident_info_serializer = ResidentInfoSerializer(data=resident_info_data)
            if resident_info_serializer.is_valid():
                resident_info_serializer.save(personId=person)
                print("ResidentInfo done")
            else:
                return Response(resident_info_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # FamilyComposition
            try:
                if 'FamilyComposition' in request.data:
                    family_composition_data = request.data.get('FamilyComposition')
                    if 'relatives' in family_composition_data and family_composition_data['relatives']:
                        relatives_data = family_composition_data.get('relatives')

                        for relative_data in relatives_data:
                            relative_serializer = FamilyCompositionSerializer(data=relative_data)
                            relativeTypeName = relative_data.get('relativeType')

                            # Assuming 'Relative' is a model with a 'relativeName' field
                            relativeType = Relative.objects.get(relativeName=relativeTypeName)

                            if relative_serializer.is_valid():
                                relative_serializer.save(personId=person, relativeType=relativeType)
                                print("family_composition done")
                            else:
                                return Response(relative_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print("No relatives provided")
                else:
                    print("FamilyComposition not provided")
            except Exception as e:
                print(f"An error occurred: {e}")

            # Education
            try:
                if 'Education' in request.data:
                    education_data = request.data.get('Education')
                    if 'educations' in education_data and education_data['educations']:
                        educations_data = education_data.get('educations')
                        for education_data in educations_data:
                            education_serializer = EducationSerializer(data=education_data)
                            if education_serializer.is_valid():
                                education_serializer.save(personId=person)
                                print("education done")
                            else:
                                return Response(education_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print("No educations provided")
                else:
                    print("Education not provided")
            except Exception as e:
                print(f"An error occurred: {e}")

            # LanguageSkill
            # LanguageSkill
            try:
                # Check if 'LanguageSkill' key is present in the request data
                if 'LanguageSkill' in request.data:
                    language_skill_data = request.data.get('LanguageSkill')

                    # Check if 'languageSkills' key is present and it's not an empty array
                    if 'languageSkills' in language_skill_data and language_skill_data['languageSkills']:
                        language_skills_data = language_skill_data.get('languageSkills')

                        for language_skill_data in language_skills_data:
                            language_skill_serializer = LanguageSkillSerializer(data=language_skill_data)

                            if language_skill_serializer.is_valid():
                                language_skill_serializer.save(personId=person)
                                print("language_skill done")
                            else:
                                return Response(language_skill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'languageSkills' key is not present or it's an empty array
                        print("No languageSkills provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'LanguageSkill' key is not present
                    print("LanguageSkill not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # AcademicDegree
            try:
                # Check if 'AcademicDegree' key is present in the request data
                if 'AcademicDegree' in request.data:
                    academic_degree_data = request.data.get('AcademicDegree')

                    # Check if 'academicDegrees' key is present and it's not an empty array
                    if 'academicDegrees' in academic_degree_data and academic_degree_data['academicDegrees']:
                        academic_degrees_data = academic_degree_data.get('academicDegrees')

                        for academic_degree_data in academic_degrees_data:
                            academic_degree_serializer = AcademicDegreeSerializer(data=academic_degree_data)

                            if academic_degree_serializer.is_valid():
                                academic_degree_serializer.save(personId=person)
                                print("academic_degree done")
                            else:
                                return Response(academic_degree_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'academicDegrees' key is not present or it's an empty array
                        print("No academicDegrees provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'AcademicDegree' key is not present
                    print("AcademicDegree not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # Course
            try:
                # Check if 'Course' key is present in the request data
                if 'Course' in request.data:
                    course_data = request.data.get('Course')

                    # Check if 'courses' key is present and it's not an empty array
                    if 'courses' in course_data and course_data['courses']:
                        courses_data = course_data.get('courses')

                        for course_data in courses_data:
                            course_serializer = CourseSerializer(data=course_data)

                            if course_serializer.is_valid():
                                course_serializer.save(personId=person)
                                print("course done")
                            else:
                                return Response(course_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'courses' key is not present or it's an empty array
                        print("No courses provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'Course' key is not present
                    print("Course not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # SportSkill
            try:
                # Check if 'SportSkill' key is present in the request data
                if 'SportSkill' in request.data:
                    sport_skill_data = request.data.get('SportSkill')

                    # Check if 'sportSkills' key is present and it's not an empty array
                    if 'sportSkills' in sport_skill_data and sport_skill_data['sportSkills']:
                        sport_skills_data = sport_skill_data.get('sportSkills')

                        for sport_skill_data in sport_skills_data:
                            sport_skill_serializer = SportSkillSerializer(data=sport_skill_data)

                            if sport_skill_serializer.is_valid():
                                sport_skill_serializer.save(personId=person)
                                print("sport_skill done")
                            else:
                                return Response(sport_skill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'sportSkills' key is not present or it's an empty array
                        print("No sportSkills provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'SportSkill' key is not present
                    print("SportSkill not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # WorkingHistory
            try:
                # Check if 'WorkingHistory' key is present in the request data
                if 'WorkingHistory' in request.data:
                    working_history_data = request.data.get('WorkingHistory')

                    # Check if 'workingHistories' key is present and it's not an empty array
                    if 'workingHistories' in working_history_data and working_history_data['workingHistories']:
                        working_histories_data = working_history_data.get('workingHistories')

                        for working_history_data in working_histories_data:
                            working_history_serializer = WorkingHistorySerializer(data=working_history_data)

                            if working_history_serializer.is_valid():
                                working_history_serializer.save(personId=person)
                                print("working_history done")
                            else:
                                return Response(working_history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'workingHistories' key is not present or it's an empty array
                        print("No workingHistories provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'WorkingHistory' key is not present
                    print("WorkingHistory not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # SpecCheckInfo
            try:
                # Check if 'SpecCheckInfo' key is present in the request data
                if 'SpecCheckInfo' in request.data:
                    spec_check_data = request.data.get('SpecCheckInfo')

                    # Check if 'specChecks' key is present and it's not an empty array
                    if 'specChecks' in spec_check_data and spec_check_data['specChecks']:
                        spec_checks_data = spec_check_data.get('specChecks')

                        for spec_check in spec_checks_data:
                            spec_check_serializer = SpecCheckSerializer(data=spec_check)

                            if spec_check_serializer.is_valid():
                                spec_check_serializer.save(personId=person)
                                print("spec check done")
                            else:
                                return Response(spec_check_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'specChecks' key is not present or it's an empty array
                        print("No specChecks provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'SpecCheckInfo' key is not present
                    print("SpecCheckInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # AttestationInfo
            try:
                # Check if 'AttestationInfo' key is present in the request data
                if 'AttestationInfo' in request.data:
                    attestation_data = request.data.get('AttestationInfo')

                    # Check if 'attestations' key is present and it's not an empty array
                    if 'attestations' in attestation_data and attestation_data['attestations']:
                        attestations = attestation_data.get('attestations')

                        for att in attestations:
                            attestation_serializer = AttestationSerializer(data=att)

                            if attestation_serializer.is_valid():
                                attestation_serializer.save(personId=person)
                                print("attestations done")
                            else:
                                return Response(attestation_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'attestations' key is not present or it's an empty array
                        print("No attestations provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'AttestationInfo' key is not present
                    print("AttestationInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # ClassCategoriesInfo
            try:
                # Check if 'ClassCategoriesInfo' key is present in the request data
                if 'ClassCategoriesInfo' in request.data:
                    class_category_data = request.data.get('ClassCategoriesInfo')

                    # Check if 'classCategories' key is present and it's not an empty array
                    if 'classCategories' in class_category_data and class_category_data['classCategories']:
                        categories = class_category_data.get('classCategories')

                        for cat in categories:
                            category_serializer = ClassCategorySerializer(data=cat)

                            if category_serializer.is_valid():
                                category_serializer.save(personId=person)
                                print("classCategories done")
                            else:
                                return Response(category_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'classCategories' key is not present or it's an empty array
                        print("No classCategories provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'ClassCategoriesInfo' key is not present
                    print("ClassCategoriesInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # AutobiographyInfo
            try:
                # Check if 'AutobiographyInfo' key is present in the request data
                if 'AutobiographyInfo' in request.data:
                    autobiography_data = request.data.get('AutobiographyInfo')

                    # Check if 'autobiographies' key is present and it's not an empty array
                    if 'autobiographies' in autobiography_data and autobiography_data['autobiographies']:
                        autos = autobiography_data.get('autobiographies')

                        for auto in autos:
                            auto_serializer = AutobiographySerializer(data=auto)

                            if auto_serializer.is_valid():
                                auto_serializer.save(personId=person)
                                print("autobiographies done")
                            else:
                                return Response(auto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'autobiographies' key is not present or it's an empty array
                        print("No autobiographies provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'AutobiographyInfo' key is not present
                    print("AutobiographyInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # RewardsInfo
            try:
                # Check if 'RewardsInfo' key is present in the request data
                if 'RewardsInfo' in request.data:
                    rewards_data = request.data.get('RewardsInfo')

                    # Check if 'rewards' key is present and it's not an empty array
                    if 'rewards' in rewards_data and rewards_data['rewards']:
                        rewards = rewards_data.get('rewards')

                        for rew in rewards:
                            rewards_serializer = RewardSerializer(data=rew)

                            if rewards_serializer.is_valid():
                                rewards_serializer.save(personId=person)
                                print("rewards done")
                            else:
                                return Response(rewards_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'rewards' key is not present or it's an empty array
                        print("No rewards provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'RewardsInfo' key is not present
                    print("RewardsInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # SickLeavesInfo
            try:
                # Check if 'SickLeavesInfo' key is present in the request data
                if 'SickLeavesInfo' in request.data:
                    sick_leaves_data = request.data.get('SickLeavesInfo')

                    # Check if 'sickLeaves' key is present and it's not an empty array
                    if 'sickLeaves' in sick_leaves_data and sick_leaves_data['sickLeaves']:
                        sick_leaves = sick_leaves_data.get('sickLeaves')

                        for sick in sick_leaves:
                            sick_leaves_serializer = SickLeaveSerializer(data=sick)

                            if sick_leaves_serializer.is_valid():
                                sick_leaves_serializer.save(personId=person)
                                print("sickLeaves done")
                            else:
                                return Response(sick_leaves_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'sickLeaves' key is not present or it's an empty array
                        print("No sickLeaves provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'SickLeavesInfo' key is not present
                    print("SickLeavesInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # InvestigationsInfo
            try:
                # Check if 'InvestigationsInfo' key is present in the request data
                if 'InvestigationsInfo' in request.data:
                    investigations_data = request.data.get('InvestigationsInfo')

                    # Check if 'investigations' key is present and it's not an empty array
                    if 'investigations' in investigations_data and investigations_data['investigations']:
                        investigations = investigations_data.get('investigations')

                        for inv in investigations:
                            inv_serializer = InvestigationSerializer(data=inv)

                            if inv_serializer.is_valid():
                                inv_serializer.save(personId=person)
                                print("investigations done")
                            else:
                                return Response(inv_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'investigations' key is not present or it's an empty array
                        print("No investigations provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'InvestigationsInfo' key is not present
                    print("InvestigationsInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            # DecreeListInfo
            try:
                # Check if 'DecreeListInfo' key is present in the request data
                if 'DecreeListInfo' in request.data:
                    decrees_data = request.data.get('DecreeListInfo')

                    # Check if 'decrees' key is present and it's not an empty array
                    if 'decrees' in decrees_data and decrees_data['decrees']:
                        decrees = decrees_data.get('decrees')

                        for dec in decrees:
                            dec_serializer = DecreeListSerializer(data=dec)

                            if dec_serializer.is_valid():
                                dec_serializer.save(personId=person)
                                print("decrees done")
                            else:
                                return Response(dec_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'decrees' key is not present or it's an empty array
                        print("No decrees provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'DecreeListInfo' key is not present
                    print("DecreeListInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            return Response(posSerializer.data, status=status.HTTP_201_CREATED)

        return Response(posSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


@csrf_exempt
def change_password(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))

            person_id = data.get('personId')
            print(person_id)
            current_password = data.get('current_password')
            new_password = data.get('new_password')
            repeat_password = data.get('repeat_password')
            Person_instance = Person.objects.get(pk=person_id)
            # Assuming CustomUser model has a field named 'person_id'
            user = CustomUser.objects.get(person_id_id=Person_instance)
            print(user)
            if user.check_password(current_password):
                if new_password == repeat_password:
                    user.set_password(new_password)
                    user.save()
                    return JsonResponse({'message': 'Password changed successfully'})
                else:
                    return JsonResponse({'error': 'New password and repeat password do not match'}, status=400)
            else:
                return JsonResponse({'error': 'Current password is incorrect'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data in the request body'}, status=400)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
