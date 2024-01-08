import io

from django.http import JsonResponse, HttpResponseServerError, HttpResponse
from django.db.models import Q
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.views.decorators.csrf import csrf_exempt
from xlsxwriter import Workbook

from birth_info.models import BirthInfo
from decree.models import SpecCheck, SickLeave, Investigation, DecreeList
from education.models import Education, Course, AcademicDegree, Attestation
from identity_card_info.models import IdentityCardInfo
from location.models import Department, Location
from military_rank.models import RankInfo, MilitaryRank
from person.models import Person, FamilyComposition, Relative, LanguageSkill, SportSkill, ClassCategory, Reward
from position.models import Position
from resident_info.models import ResidentInfo
from working_history.models import WorkingHistory


def filter_data(request):
    filtered_persons = Person.objects.all()
    filter_conditions = Q()
    educationTypeGlobal = None
    relativeTypeGlobal = None
    langNameGlobal = None
    courseTypeGlobal = None
    academicDegreeTypeGlobal = None
    sportTypeGlobal = None
    rewardTypeGlobal = None
    decreeTypeGlobal = None
    decreeSubTypeGlobal = None
    investigationDecreeTypeGlobal = None

    for key, value in request.GET.items():
        parts = key.split(':')
        if len(parts) == 3:
            model_name, field_name, field_value = parts

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
                    if value == "":
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    else:
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
                            submodelInstance = Department.objects.filter(DepartmentName__icontains=value)
                        except Department.DoesNotExist:
                            return HttpResponseServerError("Department with name {} does not exist.".format(value))
                        field_lookup = f"{model_name}__{field_name}__in"
                        filter_condition = Q(**{field_lookup: submodelInstance})
                        filter_conditions &= filter_condition
                    if field_value == 'LocationName':
                        try:
                            LocationInstance = Location.objects.filter(LocationName__icontains=value)
                        except Location.DoesNotExist:
                            return HttpResponseServerError("Location with name {} does not exist.".format(value))

                        submodelInstance = Department.objects.filter(Location__in=LocationInstance)
                        print(submodelInstance)
                        field_lookup = f"{model_name}__{field_name}__in"
                        filter_condition = Q(**{field_lookup: submodelInstance})
                        filter_conditions &= filter_condition
                        print(filter_conditions)

                if field_name == 'position':
                    if field_value == 'positionTitle':
                        try:
                            submodelInstance = Position.objects.filter(positionTitle__icontains=value)
                        except Position.DoesNotExist:
                            return HttpResponseServerError("Position with name {} does not exist.".format(value))
                        field_lookup = f"{model_name}__{field_name}__in"
                        filter_condition = Q(**{field_lookup: submodelInstance})
                        filter_conditions &= filter_condition
        if len(parts) == 2:
            model_name, field_name = parts
            print(parts)

            if "Date" in field_name or "date" in field_name:
                try:
                    start_date_str = None
                    end_date_str = None
                    dates = value.split('_')
                    if len(dates) == 1:
                        start_date_str = value
                        end_date_str = datetime.now().strftime('%Y-%m-%d')
                    if len(dates) == 2:
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
                    if value == "":
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    else:
                        start_date_str = value
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                        field_lookup = f"{model_name}__{field_name}__icontains"
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
                            relativeTypeInstance = Relative.objects.get(relativeName__icontains=value)
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
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'relJobPlace':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'birthinfo':
                    if field_name == 'country':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'city':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'region':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'languageskill':
                    if field_name == 'langName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'skillLvl':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'identitycardinfo':
                    if field_name == 'identityCardNumber':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'issuedBy':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'residentinfo':
                    if field_name == 'resCity':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'resCountry':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'resRegion':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'familyStatus':
                    if field_name == 'statusName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'gender':
                    if field_name == 'genderName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'course':
                    if field_name == 'courseType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'courseOrg':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'documentType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'courseName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'academicdegree':
                    if field_name == 'academicPlace':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'academicDegree':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'academicDiplomaNumber':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'sportskill':
                    if field_name == 'sportType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'sportSkillLvl':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'workinghistory':
                    if field_name == 'department':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'positionName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'organizationName':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'organizationAddress':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'speccheck':
                    if field_name == 'docNumber':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'attestation':
                    if field_name == 'attResult':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'classcategory':
                    if field_name == 'categoryType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'rankInfo':
                    if field_name == 'militaryRank':
                        try:
                            RankInstance = MilitaryRank.objects.get(rankTitle__icontains=value)
                        except MilitaryRank.DoesNotExist:
                            return HttpResponseServerError("MilitaryRank {} does not exist.".format(value))
                        field_lookup = f"{model_name}__{field_name}__exact"
                        filter_condition = Q(**{field_lookup: RankInstance})
                        filter_conditions &= filter_condition
                    if field_name == 'receivedType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'reward':
                    if field_name == 'rewardType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'rewardDocNumber':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'sickleave':
                    if field_name == 'sickDocNumber':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'investigation':
                    if field_name == 'investigation_decree_type':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'investigation_decree_number':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                elif model_name == 'decreelist':
                    if field_name == 'decreeType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    if field_name == 'decreeSubType':
                        field_lookup = f"{model_name}__{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition

        elif len(parts) == 1:
            field_name = parts[0]

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
                    if value == "":
                        field_lookup = f"{field_name}__icontains"
                        filter_condition = Q(**{field_lookup: value})
                        filter_conditions &= filter_condition
                    else:
                        start_date_str = value
                        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                        field_lookup = f"{field_name}__exact"
                        filter_condition = Q(**{field_lookup: start_date})
                        filter_conditions &= filter_condition
                        continue  # Skip invalid date formats
            else:
                field_lookup = f"{field_name}__icontains"
                filter_condition = Q(**{field_lookup: value})
                filter_conditions &= filter_condition

    print(filter_conditions)
    filtered_persons = filtered_persons.filter(filter_conditions).distinct()

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
            filtered_fields_model = parts[0]
            filtered_field = None
            if len(parts) == 2:
                filtered_field = parts[1]
            filtered_field_subfield = None
            if len(parts) == 3:
                filtered_field = parts[1]
                filtered_field_subfield = parts[2]

            if filtered_fields_model == 'nationality':
                nationality = p.nationality
                person_data[filtered_fields_model] = nationality

            if filtered_fields_model == 'iin':
                iin = p.iin
                person_data[filtered_fields_model] = iin

            if filtered_fields_model == 'pin':
                pin = p.pin
                person_data[filtered_fields_model] = pin

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
                    print("dsadasdsa")
                    departmentInstance = p.positionInfo.department.DepartmentName
                    person_data[filtered_field_subfield] = departmentInstance
                if filtered_field == 'department' and filtered_field_subfield == 'LocationName':
                    LocationNameInstance = p.positionInfo.department.Location.LocationName
                    person_data[filtered_field_subfield] = LocationNameInstance
                if filtered_field == 'position' and filtered_field_subfield == 'positionTitle':
                    PositionTitleInstance = p.positionInfo.position.positionTitle
                    person_data[filtered_field_subfield] = PositionTitleInstance

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
                            educationInstance = Education.objects.get(personId=p, educationPlace__icontains=value,
                                                                      educationType=educationTypeGlobal)
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
                        educationInstance = Education.objects.get(personId=p, educationType=educationTypeGlobal,
                                                                  speciality__icontains=value)
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
                        familyInstance = FamilyComposition.objects.filter(personId=p,
                                                                          relativeType=relativeTypeInstance).order_by(
                            '-id').first()
                        person_data[filtered_field] = familyInstance.relativeType.relativeName
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relName':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance,
                                                                       relName__icontains=value)
                        person_data[filtered_field] = familyInstance.relName
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relSurname':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance,
                                                                       relSurname__icontains=value)
                        person_data[filtered_field] = familyInstance.relSurname
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relPatronymic':
                    try:
                        relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                        familyInstance = FamilyComposition.objects.get(personId=p, relativeType=relativeTypeInstance,
                                                                       relPatronymic__icontains=value)
                        person_data[filtered_field] = familyInstance.relPatronymic
                    except Relative.DoesNotExist:
                        return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                if filtered_field == 'relIin':
                    if value == "":
                        try:
                            relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                            familyInstance = FamilyComposition.objects.get(personId=p,
                                                                           relativeType=relativeTypeInstance)
                            person_data[filtered_field] = familyInstance.relIin
                        except Relative.DoesNotExist:
                            return HttpResponseServerError("RelativeType {} does not exist.".format(value))
                    else:
                        try:
                            relativeTypeInstance = Relative.objects.get(relativeName=relativeTypeGlobal)
                            familyInstance = FamilyComposition.objects.get(personId=p,
                                                                           relativeType=relativeTypeInstance,
                                                                           relIin=value)
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
                if filtered_field == 'langName':  # required
                    langNameGlobal = value
                    try:
                        languageSkillInstance = LanguageSkill.objects.get(personId=p, langName__icontains=value)
                        person_data[filtered_field] = languageSkillInstance.langName
                    except LanguageSkill.DoesNotExist:
                        return HttpResponseServerError("LanguageSkill {} does not exist.".format(value))
                if filtered_field == 'skillLvl':
                    try:
                        languageSkillInstance = LanguageSkill.objects.get(personId=p,
                                                                          langName__icontains=langNameGlobal)
                        person_data[filtered_field] = languageSkillInstance.skillLvl
                    except LanguageSkill.DoesNotExist:
                        return HttpResponseServerError("LanguageSkill {} does not exist.".format(value))
            elif filtered_fields_model == 'course':
                if filtered_field == 'courseType':  # required
                    courseTypeGlobal = value
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p,
                                                                       courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        if last_course_instance is None:
                            continue
                        person_data[filtered_field] = last_course_instance.courseType
                    except Course.DoesNotExist:
                        return HttpResponseServerError("courseType {} does not exist.".format(value))
                if filtered_field == 'courseOrg':
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p, courseOrg__icontains=value,
                                                                       courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        person_data[filtered_field] = last_course_instance.courseOrg
                    except Course.DoesNotExist:
                        return HttpResponseServerError("course {} does not exist.".format(value))
                if filtered_field == 'startDate':
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p,
                                                                       courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        person_data[filtered_field] = last_course_instance.startDate
                    except Course.DoesNotExist:
                        return HttpResponseServerError("course {} does not exist.".format(value))
                if filtered_field == 'endDate':
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p,
                                                                       courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        person_data[filtered_field] = last_course_instance.endDate
                    except Course.DoesNotExist:
                        return HttpResponseServerError("courseOrg {} does not exist.".format(value))
                if filtered_field == 'documentType':
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p, documentType__icontains=value,
                                                                       courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        person_data[filtered_field] = last_course_instance.documentType
                    except Course.DoesNotExist:
                        return HttpResponseServerError("documentType {} does not exist.".format(value))
                if filtered_field == 'courseName':
                    try:
                        MultipleCourseInstance = Course.objects.filter(personId=p, courseName__icontains=value,
                                                                       courseType=courseTypeGlobal).order_by('-id')
                        last_course_instance = MultipleCourseInstance.first()
                        person_data[filtered_field] = last_course_instance.courseName
                    except Course.DoesNotExist:
                        return HttpResponseServerError("courseName {} does not exist.".format(value))
            elif filtered_fields_model == 'academicdegree':
                if filtered_field == 'academicDegree':  # required
                    academicDegreeTypeGlobal = value
                    try:
                        MultipleAcademicDegreeInstance = AcademicDegree.objects.filter(personId=p,
                                                                                       academicDegree__icontains=academicDegreeTypeGlobal).order_by(
                            '-id')
                        last_degree_instance = MultipleAcademicDegreeInstance.first()
                        if last_degree_instance is None:
                            continue
                        person_data[filtered_field] = last_degree_instance.academicDegree
                    except AcademicDegree.DoesNotExist:
                        return HttpResponseServerError("AcademicDegree {} does not exist.".format(value))
                if filtered_field == 'academicPlace':
                    try:
                        MultipleAcademicDegreeInstance = AcademicDegree.objects.filter(personId=p,
                                                                                       academicPlace__icontains=value,
                                                                                       academicDegree__icontains=academicDegreeTypeGlobal).order_by(
                            '-id')
                        last_degree_instance = MultipleAcademicDegreeInstance.first()

                        person_data[filtered_field] = last_degree_instance.academicPlace
                    except AcademicDegree.DoesNotExist:
                        return HttpResponseServerError("academicPlace {} does not exist.".format(value))
                if filtered_field == 'academicDiplomaNumber':
                    if value != "":
                        try:
                            MultipleAcademicDegreeInstance = AcademicDegree.objects.filter(personId=p,
                                                                                           academicDiplomaNumber=value,
                                                                                           academicDegree__icontains=academicDegreeTypeGlobal).order_by(
                                '-id')
                            last_degree_instance = MultipleAcademicDegreeInstance.first()
                            person_data[filtered_field] = last_degree_instance.academicDiplomaNumber
                        except AcademicDegree.DoesNotExist:
                            return HttpResponseServerError("academicDiplomaNumber {} does not exist.".format(value))
                    else:
                        try:
                            MultipleAcademicDegreeInstance = AcademicDegree.objects.filter(personId=p,
                                                                                           academicDegree__icontains=academicDegreeTypeGlobal).order_by(
                                '-id')
                            last_degree_instance = MultipleAcademicDegreeInstance.first()
                            person_data[filtered_field] = last_degree_instance.academicDiplomaNumber
                        except AcademicDegree.DoesNotExist:
                            return HttpResponseServerError("academicDiplomaNumber {} does not exist.".format(value))
                if filtered_field == 'academicDiplomaDate':
                    try:
                        MultipleAcademicDegreeInstance = AcademicDegree.objects.filter(personId=p,
                                                                                       academicDegree__icontains=academicDegreeTypeGlobal).order_by(
                            '-id')
                        last_degree_instance = MultipleAcademicDegreeInstance.first()
                        person_data[filtered_field] = last_degree_instance.academicDiplomaDate
                    except AcademicDegree.DoesNotExist:
                        return HttpResponseServerError("academicDiplomaDate {} does not exist.".format(value))
            elif filtered_fields_model == 'sportskill':
                if filtered_field == 'sportType':
                    sportTypeGlobal = value
                    try:
                        SportSkillInstance = SportSkill.objects.filter(personId=p,
                                                                       sportType__icontains=sportTypeGlobal).order_by(
                            '-id')
                        last_sport_instance = SportSkillInstance.first()
                        person_data[filtered_field] = last_sport_instance.sportType
                    except SportSkill.DoesNotExist:
                        return HttpResponseServerError("SportSkillInstance {} does not exist.".format(value))
                if filtered_field == 'sportSkillLvl':
                    try:
                        SportSkillInstance = SportSkill.objects.filter(personId=p, sportSkillLvl__icontains=value,
                                                                       sportType__icontains=sportTypeGlobal).order_by(
                            '-id')
                        last_sport_instance = SportSkillInstance.first()
                        person_data[filtered_field] = last_sport_instance.sportSkillLvl
                    except SportSkill.DoesNotExist:
                        return HttpResponseServerError("SportSkillInstance {} does not exist.".format(value))
            elif filtered_fields_model == 'workinghistory':
                if filtered_field == 'startDate':
                    try:
                        MultipleWHInstance = WorkingHistory.objects.filter(personId=p).order_by(
                            '-id')
                        last_wh_instance = MultipleWHInstance.first()
                        person_data[filtered_field] = last_wh_instance.startDate
                    except WorkingHistory.DoesNotExist:
                        return HttpResponseServerError("WorkingHistory {} does not exist.".format(value))
                if filtered_field == 'endDate':
                    try:
                        MultipleWHInstance = WorkingHistory.objects.filter(personId=p).order_by(
                            '-id')
                        last_wh_instance = MultipleWHInstance.first()
                        person_data[filtered_field] = last_wh_instance.endDate
                    except WorkingHistory.DoesNotExist:
                        return HttpResponseServerError("WorkingHistory {} does not exist.".format(value))
                if filtered_field == 'department':
                    try:
                        MultipleWHInstance = WorkingHistory.objects.filter(personId=p,
                                                                           department__icontains=value).order_by(
                            '-id')
                        last_wh_instance = MultipleWHInstance.first()
                        person_data[filtered_field] = last_wh_instance.department
                    except WorkingHistory.DoesNotExist:
                        return HttpResponseServerError("WorkingHistory {} does not exist.".format(value))
                if filtered_field == 'positionName':
                    try:
                        MultipleWHInstance = WorkingHistory.objects.filter(personId=p,
                                                                           positionName__icontains=value).order_by(
                            '-id')
                        last_wh_instance = MultipleWHInstance.first()
                        person_data[filtered_field] = last_wh_instance.positionName
                    except WorkingHistory.DoesNotExist:
                        return HttpResponseServerError("WorkingHistory {} does not exist.".format(value))
                if filtered_field == 'organizationName':
                    try:
                        MultipleWHInstance = WorkingHistory.objects.filter(personId=p,
                                                                           organizationName__icontains=value).order_by(
                            '-id')
                        last_wh_instance = MultipleWHInstance.first()
                        person_data[filtered_field] = last_wh_instance.organizationName
                    except WorkingHistory.DoesNotExist:
                        return HttpResponseServerError("WorkingHistory {} does not exist.".format(value))
                if filtered_field == 'organizationAddress':
                    try:
                        MultipleWHInstance = WorkingHistory.objects.filter(personId=p,
                                                                           organizationAddress__icontains=value).order_by(
                            '-id')
                        last_wh_instance = MultipleWHInstance.first()
                        person_data[filtered_field] = last_wh_instance.organizationAddress
                    except WorkingHistory.DoesNotExist:
                        return HttpResponseServerError("WorkingHistory {} does not exist.".format(value))
            elif filtered_fields_model == 'speccheck':
                if filtered_field == 'docNumber':
                    if value != "":
                        try:
                            MultipleSpecCheckInstance = SpecCheck.objects.filter(personId=p,
                                                                                 docNumber=value).order_by(
                                '-id')
                            last_check_instance = MultipleSpecCheckInstance.first()
                            person_data[filtered_field] = last_check_instance.docNumber
                        except SpecCheck.DoesNotExist:
                            return HttpResponseServerError("SpecCheck {} does not exist.".format(value))
                    else:
                        try:
                            MultipleSpecCheckInstance = SpecCheck.objects.filter(personId=p).order_by(
                                '-id')
                            last_check_instance = MultipleSpecCheckInstance.first()
                            person_data[filtered_field] = last_check_instance.docNumber
                        except SpecCheck.DoesNotExist:
                            return HttpResponseServerError("SpecCheck {} does not exist.".format(value))
                if filtered_field == 'docDate':
                    try:
                        MultipleSpecCheckInstance = SpecCheck.objects.filter(personId=p).order_by(
                            '-id')
                        last_check_instance = MultipleSpecCheckInstance.first()
                        person_data[filtered_field] = last_check_instance.docDate
                    except SpecCheck.DoesNotExist:
                        return HttpResponseServerError("SpecCheck {} does not exist.".format(value))
            elif filtered_fields_model == 'attestation':
                if filtered_field == 'attResult':
                    try:
                        MultipleAttrInstance = Attestation.objects.filter(personId=p,
                                                                          attResult__icontains=value).order_by(
                            '-id')
                        last_attr_instance = MultipleAttrInstance.first()
                        person_data[filtered_field] = last_attr_instance.attResult
                    except Attestation.DoesNotExist:
                        return HttpResponseServerError("Attestation {} does not exist.".format(value))
                if filtered_field == 'lastAttDate':
                    try:
                        MultipleAttrInstance = Attestation.objects.filter(personId=p).order_by(
                            '-id')
                        last_attr_instance = MultipleAttrInstance.first()
                        person_data[filtered_field] = last_attr_instance.lastAttDate
                    except Attestation.DoesNotExist:
                        return HttpResponseServerError("Attestation {} does not exist.".format(value))
                if filtered_field == 'nextAttDateMin':
                    try:
                        MultipleAttrInstance = Attestation.objects.filter(personId=p).order_by(
                            '-id')
                        last_attr_instance = MultipleAttrInstance.first()
                        person_data[filtered_field] = last_attr_instance.nextAttDateMin
                    except Attestation.DoesNotExist:
                        return HttpResponseServerError("Attestation {} does not exist.".format(value))
                if filtered_field == 'nextAttDateMax':
                    try:
                        MultipleAttrInstance = Attestation.objects.filter(personId=p).order_by(
                            '-id')
                        last_attr_instance = MultipleAttrInstance.first()
                        person_data[filtered_field] = last_attr_instance.nextAttDateMax
                    except Attestation.DoesNotExist:
                        return HttpResponseServerError("Attestation {} does not exist.".format(value))
            elif filtered_fields_model == 'classcategory':
                if filtered_field == 'categoryType':
                    try:
                        MultipleClassInstance = ClassCategory.objects.filter(personId=p,
                                                                             categoryType__icontains=value).order_by(
                            '-id')
                        last_class_instance = MultipleClassInstance.first()
                        person_data[filtered_field] = last_class_instance.categoryType
                    except ClassCategory.DoesNotExist:
                        return HttpResponseServerError("Attestation {} does not exist.".format(value))
            elif filtered_fields_model == 'rankInfo':
                if filtered_field == 'militaryRank':
                    if value != "":
                        try:
                            RankInstance = MilitaryRank.objects.get(rankTitle__icontains=value)
                            MultipleRankInfoInstance = RankInfo.objects.filter(person=p,
                                                                               militaryRank=RankInstance).order_by(
                                '-id')
                            last_rank_instance = MultipleRankInfoInstance.first()
                            person_data[filtered_field] = last_rank_instance.militaryRank.rankTitle
                        except RankInfo.DoesNotExist:
                            return HttpResponseServerError("RankInfo {} does not exist.".format(value))
                    else:
                        try:
                            MultipleRankInfoInstance = RankInfo.objects.filter(person=p).order_by(
                                '-id')
                            last_rank_instance = MultipleRankInfoInstance.first()
                            person_data[filtered_field] = last_rank_instance.militaryRank.rankTitle
                        except RankInfo.DoesNotExist:
                            return HttpResponseServerError("RankInfo {} does not exist.".format(value))
                if filtered_field == 'receivedDate':
                    try:
                        MultipleRankInfoInstance = RankInfo.objects.filter(person=p).order_by(
                            '-id')
                        last_rank_instance = MultipleRankInfoInstance.first()
                        person_data[filtered_field] = last_rank_instance.receivedDate
                    except RankInfo.DoesNotExist:
                        return HttpResponseServerError("RankInfo {} does not exist.".format(value))
                if filtered_field == 'receivedType':
                    try:
                        MultipleRankInfoInstance = RankInfo.objects.filter(person=p).order_by(
                            '-id')
                        last_rank_instance = MultipleRankInfoInstance.first()
                        person_data[filtered_field] = last_rank_instance.receivedType
                    except RankInfo.DoesNotExist:
                        return HttpResponseServerError("RankInfo {} does not exist.".format(value))
            elif filtered_fields_model == 'reward':
                if filtered_field == 'rewardType':  # required
                    rewardTypeGlobal = value
                    try:
                        MultipleRewardInstance = Reward.objects.filter(personId=p,
                                                                       rewardType__icontains=value).order_by(
                            '-id')
                        last_reward_instance = MultipleRewardInstance.first()
                        person_data[filtered_field] = last_reward_instance.rewardType
                    except Reward.DoesNotExist:
                        return HttpResponseServerError("Reward {} does not exist.".format(value))
                if filtered_field == 'rewardDocNumber':
                    try:
                        MultipleRewardInstance = Reward.objects.filter(personId=p,
                                                                       rewardType__icontains=rewardTypeGlobal).order_by(
                            '-id')
                        last_reward_instance = MultipleRewardInstance.first()
                        person_data[filtered_field] = last_reward_instance.rewardDocNumber
                    except Reward.DoesNotExist:
                        return HttpResponseServerError("Reward {} does not exist.".format(value))
                if filtered_field == 'rewardDate':
                    try:
                        MultipleRewardInstance = Reward.objects.filter(personId=p,
                                                                       rewardType__icontains=rewardTypeGlobal).order_by(
                            '-id')
                        last_reward_instance = MultipleRewardInstance.first()
                        person_data[filtered_field] = last_reward_instance.rewardDate
                    except Reward.DoesNotExist:
                        return HttpResponseServerError("Reward {} does not exist.".format(value))
            elif filtered_fields_model == 'sickleave':
                if filtered_field == 'sickDocNumber':
                    try:
                        MultipleSickLeavesInstance = SickLeave.objects.filter(personId=p,
                                                                              sickDocNumber__icontains=value).order_by(
                            '-id')
                        last_sick_instance = MultipleSickLeavesInstance.first()
                        person_data[filtered_field] = last_sick_instance.sickDocNumber
                    except SickLeave.DoesNotExist:
                        return HttpResponseServerError("SickLeave {} does not exist.".format(value))
                if filtered_field == 'sickDocDate':
                    try:
                        MultipleSickLeavesInstance = SickLeave.objects.filter(personId=p,
                                                                              sickDocDate__icontains=value).order_by(
                            '-id')
                        last_sick_instance = MultipleSickLeavesInstance.first()
                        person_data[filtered_field] = last_sick_instance.sickDocDate
                    except SickLeave.DoesNotExist:
                        return HttpResponseServerError("SickLeave {} does not exist.".format(value))
            elif filtered_fields_model == 'investigation':
                if filtered_field == 'investigation_decree_type':
                    investigationDecreeTypeGlobal = value
                    try:
                        MultipleInvInstance = Investigation.objects.filter(personId=p,
                                                                           investigation_decree_type__icontains=value).order_by(
                            '-id')
                        last_inv_instance = MultipleInvInstance.first()

                        person_data[filtered_field] = last_inv_instance.investigation_decree_type
                    except Investigation.DoesNotExist:
                        return HttpResponseServerError("Investigation {} does not exist.".format(value))
                if filtered_field == 'investigation_decree_number':
                    try:
                        MultipleInvInstance = Investigation.objects.filter(personId=p,
                                                                           investigation_decree_number__icontains=value).order_by(
                            '-id')
                        last_inv_instance = MultipleInvInstance.first()
                        if last_inv_instance is None:
                            break
                        person_data[filtered_field] = last_inv_instance.investigation_decree_number
                    except Investigation.DoesNotExist:
                        return HttpResponseServerError("Investigation {} does not exist.".format(value))
                if filtered_field == 'investigation_date':
                    try:
                        MultipleInvInstance = Investigation.objects.filter(personId=p,
                                                                           investigation_decree_type__icontains=investigationDecreeTypeGlobal
                                                                           ).order_by(
                            '-id')
                        last_inv_instance = MultipleInvInstance.first()

                        person_data[filtered_field] = last_inv_instance.investigation_date
                    except Investigation.DoesNotExist:
                        return HttpResponseServerError("Investigation {} does not exist.".format(value))


            elif filtered_fields_model == 'decreelist':
                if filtered_field == 'decreeType':  # required
                    decreeTypeGlobal = value
                    try:
                        MultipleDecreeInstance = DecreeList.objects.filter(personId=p,
                                                                           decreeType__icontains=value).order_by(
                            '-id')
                        last_dec_instance = MultipleDecreeInstance.first()

                        person_data[filtered_field] = last_dec_instance.decreeType
                    except DecreeList.DoesNotExist:
                        return HttpResponseServerError("DecreeList {} does not exist.".format(value))
                if filtered_field == 'decreeSubType':  # required
                    decreeSubTypeGlobal = value
                    try:
                        MultipleDecreeInstance = DecreeList.objects.filter(personId=p,
                                                                           decreeSubType__icontains=value).order_by(
                            '-id')
                        last_dec_instance = MultipleDecreeInstance.first()

                        person_data[filtered_field] = last_dec_instance.decreeSubType
                    except DecreeList.DoesNotExist:
                        return HttpResponseServerError("DecreeList {} does not exist.".format(value))
                if filtered_field == 'decreeDate':
                    try:
                        MultipleDecreeInstance = DecreeList.objects.filter(personId=p,
                                                                           decreeType__icontains=decreeTypeGlobal,
                                                                           decreeSubType__icontains=decreeSubTypeGlobal).order_by(
                            '-id')
                        last_dec_instance = MultipleDecreeInstance.first()

                        person_data[filtered_field] = last_dec_instance.decreeDate
                    except DecreeList.DoesNotExist:
                        return HttpResponseServerError("DecreeList {} does not exist.".format(value))

        result.append(person_data)

    return JsonResponse(result, safe=False)


@csrf_exempt
def attestation_list_view(request):
    try:
        # Extract date from query parameters
        date_param = request.GET.get('date')
        if not date_param:
            raise ValueError('Date parameter is required')

        # Convert date string to datetime object
        date = datetime.strptime(date_param, '%Y-%m-%d').date()

        # Filter Attestation objects based on date range
        attestations = Attestation.objects.filter(
            Q(nextAttDateMin__lte=date) & Q(nextAttDateMax__gte=date)
        )

        # Serialize the queryset to JSON
        data = [
            {
                'firstName': att.personId.firstName,
                'lastName': att.personId.surname,
                'patronymic': att.personId.patronymic,
                'position': att.personId.positionInfo.position.positionTitle,
                'department': att.personId.positionInfo.department.DepartmentName,
                'lastAttDate': att.lastAttDate,
                'photo': att.personId.photo_set.first().photoBinary if att.personId.photo_set.exists() else None
            }
            for att in attestations
        ]

        return JsonResponse({'data': data}, status=200)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def attestation_list_view_download(request):
    try:
        # Extract date from query parameters
        date_param = request.GET.get('date')
        if not date_param:
            raise ValueError('Date parameter is required')

        # Convert date string to datetime object
        date = datetime.strptime(date_param, '%Y-%m-%d').date()

        # Filter Attestation objects based on date range
        attestations = Attestation.objects.filter(
            Q(nextAttDateMin__lte=date) & Q(nextAttDateMax__gte=date)
        )

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()

        # Write header row
        header = ['Имя', 'Фамилия', 'Отчество', 'Должность', 'Управление', 'Дата последней аттестации']
        for col_num, header_value in enumerate(header):
            worksheet.write(0, col_num, header_value)

        # Write data rows
        for row_num, att in enumerate(attestations, start=1):
            worksheet.write(row_num, 0, att.personId.firstName)
            worksheet.write(row_num, 1, att.personId.surname)
            worksheet.write(row_num, 2, att.personId.patronymic)
            worksheet.write(row_num, 3, att.personId.positionInfo.position.positionTitle)
            worksheet.write(row_num, 4, att.personId.positionInfo.department.DepartmentName)
            worksheet.write(row_num, 5, att.lastAttDate.strftime(
                '%d.%m.%Y') if att.lastAttDate else None)

        # Close the workbook
        workbook.close()

        # Set up the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename={date}.xlsx'
        output.seek(0)
        response.write(output.getvalue())

        return response

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def rankUps_list_view(request):
    try:
        # Extract date from query parameters
        date_param = request.GET.get('date')
        if not date_param:
            raise ValueError('Date parameter is required')

        # Convert date string to datetime object
        date = datetime.strptime(date_param, '%Y-%m-%d').date()

        # Filter Person objects based on RankInfo's nextPromotionDate
        persons = Person.objects.filter(rankInfo__nextPromotionDate__range=[datetime.now().date(), date])
        # NextPromotiondate range = date - todays.daty
        # Serialize the queryset to JSON
        data = [
            {
                'firstName': person.firstName,
                'lastName': person.surname,
                'patronymic': person.patronymic,
                'position': person.positionInfo.position.positionTitle,
                'department': person.positionInfo.department.DepartmentName,
                'currentRank': person.rankInfo.militaryRank.rankTitle,
                'nextRank': person.next_rank().rankTitle if person.next_rank() else None,
                'rankUpDate': person.rankInfo.nextPromotionDate,
                'photo': person.photo_set.first().photoBinary if person.photo_set.exists() else None
            }
            for person in persons
        ]

        return JsonResponse({'data': data}, status=200)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def rankUps_list_view_download(request):
    try:
        # Extract date from query parameters
        date_param = request.GET.get('date')
        if not date_param:
            raise ValueError('Date parameter is required')

        # Convert date string to datetime object
        date = datetime.strptime(date_param, '%Y-%m-%d').date()

        # Filter Person objects based on RankInfo's nextPromotionDate
        persons = Person.objects.filter(rankInfo__nextPromotionDate__range=[datetime.now().date(), date])

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()

        # Write header row
        header = ['Имя', 'Фамилия', 'Отчество', 'Должность', 'Управление', 'Нынешнее звание', 'Следующее звание',
                  'Дата повышения']
        for col_num, header_value in enumerate(header):
            worksheet.write(0, col_num, header_value)

        # Write data rows
        for row_num, person in enumerate(persons, start=1):
            worksheet.write(row_num, 0, person.firstName)
            worksheet.write(row_num, 1, person.surname)
            worksheet.write(row_num, 2, person.patronymic)
            worksheet.write(row_num, 3, person.positionInfo.position.positionTitle)
            worksheet.write(row_num, 4, person.positionInfo.department.DepartmentName)
            worksheet.write(row_num, 5, person.rankInfo.militaryRank.rankTitle)
            worksheet.write(row_num, 6, person.next_rank().rankTitle if person.next_rank() else None)
            worksheet.write(row_num, 7, person.rankInfo.nextPromotionDate.strftime(
                '%d.%m.%Y') if person.rankInfo.nextPromotionDate else None)

        # Close the workbook
        workbook.close()

        # Set up the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=rank_ups_data.xlsx'
        output.seek(0)
        response.write(output.getvalue())

        return response

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def pension_list_view(request):
    try:
        # Extract date from query parameters
        date_param = request.GET.get('date')
        if not date_param:
            raise ValueError('Date parameter is required')

        # Convert date string to datetime object
        date = datetime.strptime(date_param, '%Y-%m-%d').date()

        # Retrieve persons with birth info
        persons = Person.objects.filter(birthinfo__isnull=False)

        # Create a list of persons close to pension age within 1 month based on the given request date
        data = [
            {
                'firstName': person.firstName,
                'lastName': person.surname,
                'patronymic': person.patronymic,
                'position': person.positionInfo.position.positionTitle,
                'department': person.positionInfo.department.DepartmentName,
                'currentRank': person.rankInfo.militaryRank.rankTitle,
                'photo': person.photo_set.first().photoBinary if person.photo_set.exists() else None,
                'age': (date - person.birthinfo_set.first().birth_date).days // 365,
                'pensionDate': (person.birthinfo_set.first().birth_date.replace(year=person.birthinfo_set.first().birth_date.year + person.rankInfo.militaryRank.pensionAge)).strftime('%Y-%m-%d'),
            }
            for person in persons
            if (
                person.birthinfo_set.first().birth_date <= date - relativedelta(years=person.rankInfo.militaryRank.pensionAge) <= date
            ) and ((date - (relativedelta(years=person.rankInfo.militaryRank.pensionAge) + person.birthinfo_set.first().birth_date)).days <= 30)
        ]

        return JsonResponse({'data': data}, status=200)

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
def pension_list_view_download(request):
    try:
        # Extract date from query parameters
        date_param = request.GET.get('date')
        if not date_param:
            raise ValueError('Date parameter is required')

        # Convert date string to datetime object
        date = datetime.strptime(date_param, '%Y-%m-%d').date()

        # Retrieve persons with birth info, filtered based on pension conditions
        persons = Person.objects.filter(
            birthinfo__isnull=False,
            rankInfo__militaryRank__pensionAge__isnull=False,
        )

        # Create an in-memory Excel file
        output = io.BytesIO()
        workbook = Workbook(output)
        worksheet = workbook.add_worksheet()

        # Write header row
        header = ['Имя', 'Фамилия', 'Отчество', 'Должность', 'Управление', 'Нынешнее звание', 'Возраст', 'Дата пенсии']
        for col_num, header_value in enumerate(header):
            worksheet.write(0, col_num, header_value)

        # Write data rows
        for row_num, person in enumerate(persons, start=1):
            age = (date - person.birthinfo_set.first().birth_date).days // 365
            pension_age = person.rankInfo.militaryRank.pensionAge
            pension_date = person.birthinfo_set.first().birth_date.replace(year=person.birthinfo_set.first().birth_date.year + pension_age)

            if person.birthinfo_set.first().birth_date <= date - relativedelta(years=pension_age) <= date and (date - pension_date).days <= 30:
                worksheet.write(row_num, 0, person.firstName)
                worksheet.write(row_num, 1, person.surname)
                worksheet.write(row_num, 2, person.patronymic)
                worksheet.write(row_num, 3, person.positionInfo.position.positionTitle)
                worksheet.write(row_num, 4, person.positionInfo.department.DepartmentName)
                worksheet.write(row_num, 5, person.rankInfo.militaryRank.rankTitle)
                worksheet.write(row_num, 6, age)  # Age
                worksheet.write(row_num, 7, pension_date.strftime('%Y-%m-%d'))  # Pension Date

        # Close the workbook
        workbook.close()

        # Set up the response
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=pension_list_data.xlsx'
        output.seek(0)
        response.write(output.getvalue())

        return response

    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)