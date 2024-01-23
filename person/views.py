import base64
import json
from datetime import datetime, timedelta, date

from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
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
from military_rank.models import MilitaryRank
from military_rank.serializers import RankInfoSerializer
from photo.serializers import PhotoSerializer
from position.models import Position

from position.serializers import PositionInfoSerializer
from resident_info.models import ResidentInfo
from resident_info.serializers import ResidentInfoSerializer
from working_history.models import WorkingHistory
from working_history.serializers import WorkingHistorySerializer
from .models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, Reward, \
    LanguageSkill, SportSkill, CustomUser, RankArchive
from .serializers import PersonSerializer, GenderSerializer, FamilyStatusSerializer, RelativeSerializer, \
    FamilyCompositionSerializer, ClassCategorySerializer, AutobiographySerializer, RewardSerializer, \
    LanguageSkillSerializer, SportSkillSerializer, RankArchiveSerializer
from rest_framework.pagination import PageNumberPagination


@csrf_exempt
def departments_persons(request, *args, **kwargs):
    try:

        department = request.GET.get('departmentId', None)
        department = Department.objects.get(pk=department)
        persons = Person.objects.filter(positionInfo__department=department)

        serializer = PersonSerializer(persons, many=True)

        return JsonResponse({'persons': serializer.data})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    @action(detail=True, methods=['PATCH'])
    def update_family_status(self, request):
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
    def update_gender(self, request):
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

        rankArchieve_objects = RankArchive.objects.filter(personId=person.id)
        rankArchieve_data = RankArchiveSerializer(rankArchieve_objects, many=True).data

        working_history_objects = WorkingHistory.objects.filter(personId=person.id).order_by('-startDate')
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
            'WorkingHistory': {
                'workingHistories': working_history_data
            },
            'RankArchive': {
                'archiveObjects': rankArchieve_data
            },
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
        if posSerializer.is_valid():
            # Create the Person instance
            positionInfoData = request.data.get('PositionInfo')

            positionName = positionInfoData.get('position')
            positionInstance = Position.objects.get(positionTitle=positionName)

            departmentName = positionInfoData.get('department')
            try:
                departmentInstance = Department.objects.get(DepartmentName=departmentName)
            except Department.DoesNotExist:
                departmentInstance = None

            rankInfo = None

            try:
                rankSerializer = RankInfoSerializer(data=request.data.get('RankInfo'))
                rankInfoData = request.data.get('RankInfo')
                rankName = rankInfoData.get('militaryRank')
                receivedType = rankInfoData.get('receivedType')
                receivedDate = rankInfoData.get('receivedDate')
                rankInstance = MilitaryRank.objects.get(rankTitle=rankName)

                rank_info_data = {
                    'militaryRank': rankInstance,
                    'receivedType': receivedType,
                    'receivedDate': receivedDate,
                }

                rankInfo = rankSerializer.create(validated_data=rank_info_data)

            except Exception as e:
                # Handle other exceptions if necessary
                print(f"Person have no Rank ok: {e}")
            # Use create method instead of save
            if departmentInstance is not None:
                posInfo = posSerializer.save(position=positionInstance, department=departmentInstance)
            else:
                posInfo = posSerializer.save(position=positionInstance, department=None)

            person_data = request.data.get('Person')
            genderName = person_data.get('gender')
            genderInstance = Gender.objects.get(genderName=genderName)
            familyStatusName = person_data.get('familyStatus')
            familyStatusInstance = FamilyStatus.objects.get(statusName=familyStatusName)

            person_serializer = PersonSerializer(data=person_data)

            if person_serializer.is_valid():
                person = person_serializer.save(positionInfo=posInfo, gender=genderInstance,
                                                rankInfo=rankInfo,
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
                        # 'photoBinary' is empty or not present
                        print("No photoBinary provided. Using default PNG photo.")

                        # Load default PNG photo
                        default_photo_path = "person/static/images/defaultPerson.png"
                        with open(default_photo_path, "rb") as f:
                            content = f.read()
                            encoded_photo = base64.b64encode(content).decode('utf-8')

                        # Assign the encoded string to 'photoBinary' field
                        photo_data['photoBinary'] = encoded_photo

                        # Save the default photo
                        photo_serializer = PhotoSerializer(data=photo_data)
                        if photo_serializer.is_valid():
                            photo_serializer.save(personId=person)
                            print("Default Photo saved")
                        else:
                            return Response(photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # 'Photo' key is not present
                    print("Photo not provided. Using default PNG photo.")

                    # Load default PNG photo
                    default_photo_path = "person/static/images/defaultPerson.png"
                    with open(default_photo_path, "rb") as f:
                        content = f.read()
                        encoded_photo = base64.b64encode(content).decode('utf-8')

                    # Create a new 'Photo' dictionary with the encoded photo
                    default_photo_data = {'photoBinary': encoded_photo, 'personId': person.id}

                    # Save the default photo
                    default_photo_serializer = PhotoSerializer(data=default_photo_data)
                    if default_photo_serializer.is_valid():
                        default_photo_serializer.save()
                        print("Default Photo saved")
                    else:
                        return Response(default_photo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
                    family_composition_data = request.data['FamilyComposition']
                    if 'relatives' in family_composition_data and family_composition_data['relatives']:
                        relatives_data = family_composition_data.get('relatives')

                        for relative_data in relatives_data:
                            relativeTypeName = relative_data.get('relativeType')
                            relativeType = Relative.objects.get(relativeName=relativeTypeName)
                            relative = {
                                'id': relativeType.id,
                                'relativeName': relativeType.relativeName
                            }
                            relative_data['relativeType'] = relative

                            relative_serializer = FamilyCompositionSerializer(data=relative_data)
                            if relative_serializer.is_valid():
                                relative_serializer.save(personId=person, relativeType=relative)
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
                    education_data = request.data['Education']
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
                    language_skill_data = request.data['LanguageSkill']

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
                        # Handle the case where 'languageSkills' key is not present
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
                    academic_degree_data = request.data['AcademicDegree']

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
                        # Handle the case where 'academicDegrees' key is not present
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
                    course_data = request.data['Course']

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
                        # Handle the case where 'courses' key is not present
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
                    sport_skill_data = request.data['SportSkill']

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
                        # Handle the case where 'sportSkills' key is not present
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
                    working_history_data = request.data['WorkingHistory']

                    # Check if 'workingHistories' key is present and it's not an empty array
                    if 'workingHistories' in working_history_data:
                        working_histories_data = working_history_data.get('workingHistories')

                        for working_history_data in working_histories_data:
                            working_history_serializer = WorkingHistorySerializer(data=working_history_data)

                            if working_history_serializer.is_valid():
                                working_history_serializer.save(personId=person)
                                print("working_history done")
                            else:
                                return Response(working_history_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'workingHistories' key is not present
                        print("No workingHistories provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'WorkingHistory' key is not present
                    print("WorkingHistory not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")
            if posInfo.department is not None:
                WorkingHistory.objects.create(
                    positionName=str(posInfo.position.positionTitle),
                    startDate=posInfo.receivedDate,
                    personId=person,
                    department=posInfo.department.DepartmentName,
                    organizationName="АФМ",
                    organizationAddress="Бейбітшілік 10"
                    # Add other fields from PositionInfo as needed
                )
            else:
                WorkingHistory.objects.create(
                    positionName=str(posInfo.position.positionTitle),
                    startDate=posInfo.receivedDate,
                    personId=person,
                    department=None,
                    organizationName="АФМ",
                    organizationAddress="Бейбітшілік 10"
                    # Add other fields from PositionInfo as needed
                )
            if rankInfo is not None:
                RankArchive.objects.create(
                    personId=person,
                    militaryRank=rankInfo.militaryRank,
                    receivedType=rankInfo.receivedType,
                    decreeNumber=rankInfo.decreeNumber,
                    startDate=rankInfo.receivedDate,
                    endDate=None
                )

            # SpecCheckInfo
            try:
                # Check if 'SpecCheckInfo' key is present in the request data
                if 'SpecCheckInfo' in request.data:
                    spec_check_data = request.data['SpecCheckInfo']

                    # Check if 'specChecks' key is present and it's not an empty array
                    if 'specChecks' in spec_check_data:
                        spec_checks_data = spec_check_data.get('specChecks')

                        for spec_check in spec_checks_data:
                            spec_check_serializer = SpecCheckSerializer(data=spec_check)

                            if spec_check_serializer.is_valid():
                                spec_check_serializer.save(personId=person)
                                print("spec check done")
                            else:
                                return Response(spec_check_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # Handle the case where 'specChecks' key is not present
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
                    attestation_data = request.data['AttestationInfo']

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
                        # Handle the case where 'attestations' key is not present
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
                    class_category_data = request.data['ClassCategoriesInfo']

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
                        # Handle the case where 'classCategories' key is not present
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
                    autobiography_data = request.data['AutobiographyInfo']

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
                        # Handle the case where 'autobiographies' key is not present
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
                    rewards_data = request.data['RewardsInfo']

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
                        # Handle the case where 'rewards' key is not present
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
                    sick_leaves_data = request.data['SickLeavesInfo']

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
                        # Handle the case where 'sickLeaves' key is not present
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
                    investigations_data = request.data['InvestigationsInfo']

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
                        # Handle the case where 'investigations' key is not present
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
                    decrees_data = request.data['DecreeListInfo']

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
                        # Handle the case where 'decrees' key is not present
                        print("No decrees provided")
                        # You may choose to return a response or perform other actions
                else:
                    # Handle the case where 'DecreeListInfo' key is not present
                    print("DecreeListInfo not provided")
                    # You may choose to return a response or perform other actions
            except Exception as e:
                # Handle other exceptions if necessary
                print(f"An error occurred: {e}")

            return Response("Person created successfully")

        return Response(posSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def search_persons(request):
    if request.method == 'GET':
        search_query = request.GET.get('q', '').strip()

        # Split the search query into separate terms
        search_terms = search_query.split()

        # Define search fields
        search_fields = ['firstName__icontains', 'surname__icontains', 'patronymic__icontains']

        # Use Q objects to create OR conditions for each search field and term
        query = Q()
        for term in search_terms:
            for field in search_fields:
                query |= Q(**{field: term})

        persons = Person.objects.filter(query)

        # You can serialize the persons to JSON and return it
        persons_data = [
            {
                'id': person.id,
                'firstName': person.firstName,
                'surname': person.surname,
                'patronymic': person.patronymic,
                'photo': person.photo_set.first().photoBinary if person.photo_set.exists() else None,
                'currentRank': person.rankInfo.militaryRank.rankTitle
            }
            for person in persons
        ]

        return JsonResponse({'persons': persons_data})

    return JsonResponse({'error': 'Invalid request method'})


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

    def create(self, request, *args, **kwargs):
        # Extract the data for the nested serializer (RelativeSerializer)
        relativeTypeName = request.data.get('relativeType')
        relativeType = Relative.objects.get(relativeName=relativeTypeName)
        relative = {
            'id': relativeType.id,
            'relativeName': relativeType.relativeName
        }
        request.data['relativeType'] = relative

        relativeInstance = Relative.objects.get(relativeName=request.data['relativeType']['relativeName'])
        personInstance = Person.objects.get(pk=request.data['personId'])
        family_composition = FamilyComposition.objects.create(
            relName=request.data['relName'],
            relSurname=request.data['relSurname'],
            relPatronymic=request.data['relPatronymic'],
            relIin=request.data['relIin'],
            relBirthDate=request.data['relBirthDate'],
            relJobPlace=request.data['relJobPlace'],
            personId=personInstance,
            relativeType=relativeInstance
        )

        return Response(
            {"message": "family_composition done", "data": FamilyCompositionSerializer(family_composition).data},
            status=status.HTTP_201_CREATED)


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

            # Assuming CustomUser model has a field named 'person_id'
            user = CustomUser.objects.get(person_id=person_id)
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


def get_rank_up_info(request):
    # Get test_date from query parameters, defaulting to today's date if not provided
    test_date_param = request.GET.get('test_date')
    test_date = datetime.strptime(test_date_param, '%Y-%m-%d').date() if test_date_param else date.today()

    # Get persons who need to rank up
    persons_to_rank_up = Person.objects.filter(
        rankInfo__nextPromotionDate__lte=test_date + timedelta(days=30)
    )

    # Extract relevant information for response
    rank_up_data = []
    for person in persons_to_rank_up:
        person_data = {
            'firstName': person.firstName,
            'surname': person.surname,
            'patronymic': person.patronymic,
            'photo': person.photo_set.first().photoBinary if person.photo_set.exists() else None,
            # Assuming 'photo' is a FileField
        }
        rank_up_data.append(person_data)

    response_data = {
        'count': len(rank_up_data),
        'persons': rank_up_data,
    }

    return JsonResponse(response_data)


@require_GET
def getAvailableLastPin(request):
    # Get the last person
    last_person = Person.objects.order_by('-id').first()

    if last_person is None:
        response_data = {
            'newPin': '00100001',
        }
        return JsonResponse(response_data)

    # Extract the numeric part of the last person's pin
    last_pin_numeric = int(last_person.pin[3:])

    # Increment the numeric part
    new_pin_numeric = last_pin_numeric + 1

    # Format the new pin with leading zeros
    new_pin = f'001{new_pin_numeric:05d}'

    # Prepare the response data
    response_data = {
        'newPin': new_pin,
    }

    return JsonResponse(response_data)
