from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse, HttpResponseServerError
from django.db.models import Q
from datetime import datetime

from birth_info.models import BirthInfo
from education.models import Education, Course
from identity_card_info.models import IdentityCardInfo
from location.models import Department, Location
from person.models import Person, Gender, FamilyComposition, Relative, LanguageSkill
from person.serializers import PersonSerializer
from position.models import PositionInfo, Position
from resident_info.models import ResidentInfo


def filter_data(request):
    filtered_persons = Person.objects.all()
    filter_conditions = Q()
    filtered_fields = []
    educationTypeGlobal = None
    relativeTypeGlobal = None
    langNameGlobal = None
    courseTypeGlobal = None
    academicDegreeTypeGlobal = None
    sportTypeGlobal = None

    for key, value in request.GET.items():
        parts = key.split(':')
        if len(parts) == 3:
            model_name, field_name, field_value = parts
            if value == '':
                # If the value is empty, skip filtering for this field
                continue
            if "Date" in field_name or "date" in field_name:
                try:
                    start_date_str, end_date_str = value.split('_')
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if start_date == end_date:
                        # If the start_date and end_date are the same, it's an exact date match
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                    else:
                        # Otherwise, it's a date range filter
                        field_lookup = f"{model_name}__{field_name}__range"
                        filter_condition = Q(**{field_lookup: [start_date, end_date]})
                    filter_conditions &= filter_condition
                except ValueError:
                    start_date_str = value
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    field_lookup = f"{model_name}__{field_name}__exact"
                    filter_condition = Q(**{field_lookup: start_date})
                    filter_conditions &= filter_condition
                    continue  # Skip invalid date formats
            else:
                # For non-date fields, use an exact match
                if field_name == 'department':
                    if field_value == 'DepartmentName':
                        try:
                            submodelInstance = Department.objects.get(DepartmentName=value)
                        except Department.DoesNotExist:
                            return HttpResponseServerError("Department with name {} does not exist.".format(value))
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: submodelInstance})
                        filter_conditions &= filter_condition
                    if field_value == 'LocationName':
                        try:
                            LocationInstance = Location.objects.get(LocationName=value)
                        except Location.DoesNotExist:
                            return HttpResponseServerError("Location with name {} does not exist.".format(value))

                        submodelInstance = Department.objects.filter(Location=LocationInstance)
                        field_lookup = f"{model_name}__{field_name}__in"
                        filter_condition = Q(**{field_lookup: submodelInstance})
                        filter_conditions &= filter_condition

                if field_name == 'position':
                    if field_value == 'positionTitle':
                        try:
                            submodelInstance = Position.objects.get(positionTitle=value)
                        except Position.DoesNotExist:
                            return HttpResponseServerError("Position with name {} does not exist.".format(value))
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: submodelInstance})
                        filter_conditions &= filter_condition
        if len(parts) == 2:
            model_name, field_name = parts

            if value == '':
                # If the value is empty, skip filtering for this field
                continue
            if "Date" in field_name or "date" in field_name:
                try:
                    start_date_str, end_date_str = value.split('_')
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if start_date == end_date:
                        # If the start_date and end_date are the same, it's an exact date match
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                    else:
                        # Otherwise, it's a date range filter
                        field_lookup = f"{model_name}__{field_name}__range"
                        filter_condition = Q(**{field_lookup: [start_date, end_date]})
                    filter_conditions &= filter_condition
                except ValueError:
                    start_date_str = value
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    field_lookup = f"{model_name}__{field_name}__exact"
                    filter_condition = Q(**{field_lookup: start_date})
                    filter_conditions &= filter_condition
                    continue  # Skip invalid date formats
            else:
                # For non-date fields, use an exact match
                if model_name == 'education':
                    if field_name == 'educationPlace':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'speciality':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'familycomposition':
                    if field_name == 'relativeType':
                        try:
                            relativeTypeInstance = Relative.objects.get(relativeName=value)
                        except Relative.DoesNotExist:
                            return HttpResponseServerError("Relative type does not exist")
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: relativeTypeInstance})
                        filter_conditions &= filter_condition
                    if field_name == 'relName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'relSurname':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'relPatronymic':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'relIin':
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'relJobPlace':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition

                elif model_name == 'course':
                    if field_name == 'courseOrg':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition



        elif len(parts) == 1:
            field_name = parts[0]
            if value == '':
                # If the value is empty, skip filtering for this field
                continue
            if "Date" in field_name or "date" in field_name:
                try:
                    start_date_str, end_date_str = value.split('_')
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if start_date == end_date:
                        # If the start_date and end_date are the same, it's an exact date match
                        field_lookup = f"{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                    else:
                        # Otherwise, it's a date range filter
                        field_lookup = f"{field_name}__range"
                        filter_condition = Q(**{field_lookup: [start_date, end_date]})
                    filter_conditions &= filter_condition
                except ValueError:
                    start_date_str = value
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    field_lookup = f"{field_name}__exact"
                    filter_condition = Q(**{field_lookup: start_date})
                    filter_conditions &= filter_condition
                    continue  # Skip invalid date formats
            else:
                # For non-date fields, use an exact match
                field_lookup = f"{field_name}__exact"
                filter_condition = Q(**{field_lookup: value})
                filter_conditions &= filter_condition

    filtered_persons = filtered_persons.filter(filter_conditions)

    # Serialize the required fields along with the filtered field
    result = []
    for p in filtered_persons:
        person_data = {
            "id": p.id,
            "surname": p.surname,
            "firstName": p.firstName,
            "patronymic": p.patronymic,
        }
        # Include the filtered field in the response

        for key, value in request.GET.items():
            parts = key.split(":")
            if len(parts) == 1:
                continue

            filtered_fields_model = parts[0]
            filtered_field = parts[1]
            filtered_field_subfield = None
            if len(parts) == 3:
                filtered_field_subfield = parts[2]

            if filtered_fields_model == 'gender':
                if filtered_field == 'genderName':
                    genderNameInstance = p.gender.genderName
                    person_data[filtered_field] = genderNameInstance

            elif filtered_fields_model == 'familyStatus':
                if filtered_field == 'statusName':
                    statusNameInstance = p.familyStatus.statusName
                    person_data[filtered_field] = statusNameInstance

            elif filtered_fields_model == 'birthinfo':
                if filtered_field == 'birth_date':
                    BirthDateInstance = BirthInfo.objects.get(personId=p).birth_date
                    person_data[filtered_field] = BirthDateInstance
                if filtered_field == 'country':
                    BirthCountryInstance = BirthInfo.objects.get(personId=p).country
                    person_data[filtered_field] = BirthCountryInstance
                if filtered_field == 'city':
                    BirthCityInstance = BirthInfo.objects.get(personId=p).city
                    person_data[filtered_field] = BirthCityInstance
                if filtered_field == 'region':
                    BirthRegionInstance = BirthInfo.objects.get(personId=p).region
                    person_data[filtered_field] = BirthRegionInstance

            elif filtered_fields_model == 'residentinfo':
                if filtered_field == 'resCountry':
                    resCountryInstance = ResidentInfo.objects.get(personId=p).resCountry
                    person_data[filtered_field] = resCountryInstance
                if filtered_field == 'resCity':
                    resCityInstance = ResidentInfo.objects.get(personId=p).resCity
                    person_data[filtered_field] = resCityInstance
                if filtered_field == 'resRegion':
                    resRegionInstance = ResidentInfo.objects.get(personId=p).resRegion
                    person_data[filtered_field] = resRegionInstance

            elif filtered_fields_model == 'identitycardinfo':
                if filtered_field == 'identityCardNumber':
                    identityCardNumberInstance = IdentityCardInfo.objects.get(personId=p).identityCardNumber
                    person_data[filtered_field] = identityCardNumberInstance
                if filtered_field == 'issuedBy':
                    issuedByInstance = IdentityCardInfo.objects.get(personId=p).issuedBy
                    person_data[filtered_field] = issuedByInstance
                if filtered_field == 'dateOfIssue':
                    dateOfIssueInstance = IdentityCardInfo.objects.get(personId=p).dateOfIssue
                    person_data[filtered_field] = dateOfIssueInstance

            elif filtered_fields_model == 'positionInfo':
                if filtered_field == 'department' and filtered_field_subfield == 'DepartmentName':
                    departmentInstance = p.positionInfo.department.DepartmentName
                    person_data[filtered_field] = departmentInstance
                if filtered_field == 'department' and filtered_field_subfield == 'LocationName':
                    LocationNameInstance = p.positionInfo.department.Location.LocationName
                    person_data[filtered_field+filtered_field_subfield] = LocationNameInstance
                if filtered_field == 'position' and filtered_field_subfield == 'positionTitle':
                    PositionTitleInstance = p.positionInfo.position.positionTitle
                    person_data[filtered_field] = PositionTitleInstance

            elif filtered_fields_model == 'education':

                if filtered_field == 'educationType':
                    educationTypeGlobal = value
                    try:
                        educationInstance = Education.objects.get(personId=p, educationType=value)
                        person_data[filtered_field] = educationInstance.educationType
                    except Education.DoesNotExist:
                        return HttpResponseServerError("EducationType {} does not exist.".format(value))
                if filtered_field == 'educationPlace':
                    if value == "":
                        try:
                            educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal)
                            person_data[filtered_field] = educationInstance.educationPlace
                        except Education.DoesNotExist:
                            return HttpResponseServerError("Education Type is required")
                    else:
                        try:
                            educationInstance = Education.objects.get(personId=p, educationPlace__icontains=value, educationType=educationTypeGlobal)
                            person_data[filtered_field] = educationInstance.educationPlace
                        except Education.DoesNotExist:
                            return HttpResponseServerError("Education does not exist")
                if filtered_field == 'educationDateIn':
                    try:
                        educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal)
                        person_data[filtered_field] = educationInstance.educationDateIn
                    except Education.DoesNotExist:
                        return HttpResponseServerError("Education does not exist")
                if filtered_field == 'educationDateOut':
                    try:
                        educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal)
                        person_data[filtered_field] = educationInstance.educationDateOut
                    except Education.DoesNotExist:
                        return HttpResponseServerError("Education does not exist")
                if filtered_field == 'speciality':
                    try:
                        educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal, speciality__icontains=value)
                        person_data[filtered_field] = educationInstance.speciality
                    except Education.DoesNotExist:
                        return HttpResponseServerError("Education does not exist")
                if filtered_field == 'diplomaNumber':
                    if value == "":
                        try:
                            educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal)
                            person_data[filtered_field] = educationInstance.diplomaNumber
                        except Education.DoesNotExist:
                            return HttpResponseServerError("Education does not exist")
                    else:
                        try:
                            educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal,
                                                                      diplomaNumber=value)
                            person_data[filtered_field] = educationInstance.diplomaNumber
                        except Education.DoesNotExist:
                            return HttpResponseServerError("Education does not exist")

            elif filtered_fields_model == 'familycomposition':
                if filtered_field == 'relativeType':
                    relativeTypeGlobal = value
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance)
                        person_data[filtered_field] = familyInstance.relativeType.relativeName
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relName':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance, relName__icontains=value)
                        person_data[filtered_field] = familyInstance.relName
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relSurname':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance, relSurname__icontains=value)
                        person_data[filtered_field] = familyInstance.relSurname
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relPatronymic':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance, relPatronymic__icontains=value)
                        person_data[filtered_field] = familyInstance.relPatronymic
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relIin':
                    if value == "":
                        try:
                            relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                            familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance)
                            person_data[filtered_field] = familyInstance.relIin
                        except Relative.DoesNotExist:
                            return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                    else:
                        try:
                            relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                            familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance, relIin=value)
                            person_data[filtered_field] = familyInstance.relIin
                        except Relative.DoesNotExist:
                            return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relBirthDate':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance)
                        person_data[filtered_field] = familyInstance.relBirthDate
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relJobPlace':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance)
                        person_data[filtered_field] = familyInstance.relJobPlace
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
            elif filtered_fields_model == 'languageskill':
                if filtered_field == 'langName': #required
                    langNameGlobal = value
                    try:
                        languageSkillInstance = LanguageSkill.objects.get(personId=p, langName=value)
                        person_data[filtered_field] = languageSkillInstance.langName
                    except LanguageSkill.DoesNotExist:
                        return HttpResponseServerError("LanguageSkill {} does not exist.".format(value))
                if filtered_field == 'skillLvl':
                    try:
                        languageSkillInstance = LanguageSkill.objects.get(personId=p, langName=langNameGlobal)
                        person_data[filtered_field] = languageSkillInstance.skillLvl
                    except LanguageSkill.DoesNotExist:
                        return HttpResponseServerError("LanguageSkill {} does not exist.".format(value))
            elif filtered_fields_model == 'course':
                if filtered_field == 'courseType':
                    courseTypeGlobal = value
                if filtered_field == 'courseOrg':
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p, courseOrg__icontains=value, courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        print(last_course_instance)
                        person_data[filtered_field] = last_course_instance.courseOrg
                    except Course.DoesNotExist:
                        return HttpResponseServerError("courseOrg {} does not exist.".format(value))
        result.append(person_data)

    return JsonResponse(result, safe=False)
