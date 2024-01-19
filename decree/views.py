import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from staffing_table.models import StaffingTable, Vacancy
from location.models import Department
from military_rank.models import MilitaryRank, RankInfo
from person.models import RankArchive
from photo.models import Photo
from position.models import PositionInfo, Position
from working_history.models import WorkingHistory
from .models import DecreeList, SpecCheck, SickLeave, Investigation, TransferInfo, RankUpInfo, AppointmentInfo
from .serializers import DecreeListSerializer, SpecCheckSerializer, SickLeaveSerializer, InvestigationSerializer


def getDecreeList(request):
    # Get all decrees from DecreeList model
    decrees = DecreeList.objects.all()

    # Serialize the decree data
    decree_data = []
    for decree in decrees:
        person_data = {
            'iin': decree.personId.iin,
            'pin': decree.personId.pin,
            'surname': decree.personId.surname,
            'firstName': decree.personId.firstName,
            'patronymic': decree.personId.patronymic,
            'positionInfo': decree.personId.positionInfo.position.positionTitle,
            'rankInfo': decree.personId.rankInfo.militaryRank.rankTitle,
        }

        # Get the photo for the person
        photo = Photo.objects.filter(personId=decree.personId).first()
        if photo:
            person_data['photo'] = photo.photoBinary
        else:
            person_data['photo'] = None

        decree_data.append({
            'decreeId': decree.id,
            'decreeType': decree.decreeType,
            'decreeNumber': decree.decreeNumber,
            'decreeDate': decree.decreeDate,
            'decreeIsConfirmed': decree.isConfirmed,
            'person': person_data,
        })

    return JsonResponse({'decrees': decree_data})


@csrf_exempt
def getDecreeInfo(request):
    decreeId = request.GET.get('decreeId')

    try:
        decreeInstance = DecreeList.objects.get(pk=decreeId)
    except DecreeList.DoesNotExist:
        return JsonResponse({'error': 'Decree not found'})

    person_data = {
        'iin': decreeInstance.personId.iin,
        'pin': decreeInstance.personId.pin,
        'surname': decreeInstance.personId.surname,
        'firstName': decreeInstance.personId.firstName,
        'patronymic': decreeInstance.personId.patronymic,
        'positionInfo': decreeInstance.personId.positionInfo.position.positionTitle,
        'rankInfo': decreeInstance.personId.rankInfo.militaryRank.rankTitle,
    }

    # Get the photo for the person
    photo = Photo.objects.filter(personId=decreeInstance.personId).first()
    if photo:
        person_data['photo'] = photo.photoBinary
    else:
        person_data['photo'] = None

    if decreeInstance.decreeType == 'Назначение':
        decreeInfo = AppointmentInfo.objects.get(decreeId=decreeInstance)

        appointmentInfo = [{
            'decreeInfo': {
                'decreeId': decreeInstance.id,
                'decreeType': decreeInstance.decreeType,
                'decreeNumber': decreeInstance.decreeNumber,
                'decreeDate': decreeInstance.decreeDate,
                'person': person_data,
            },
            'newPosition': {
                'newDepartment': decreeInfo.appointmentDepartment.DepartmentName,
                'newPosition': decreeInfo.appointmentPosition.positionTitle,
                'probationMonthCount': decreeInfo.appointmentProbation,
                'base': decreeInfo.appointmentBase,
                'appointmentType': decreeInfo.appointmentType
            }

        }]

        return JsonResponse({'appointmentInfo': appointmentInfo})

    if decreeInstance.decreeType == 'Перемещение':

        decreeInfo = TransferInfo.objects.get(decreeId=decreeInstance)

        transfer_info = [{
            'decreeInfo': {
                'decreeId': decreeInstance.id,
                'decreeType': decreeInstance.decreeType,
                'decreeNumber': decreeInstance.decreeNumber,
                'decreeDate': decreeInstance.decreeDate,
                'person': person_data,
            },
            'newPosition': {
                'newDepartment': decreeInfo.newDepartment.DepartmentName,
                'newPosition': decreeInfo.newPosition.positionTitle
            },
            'previousPosition': {
                'previousDepartment': decreeInfo.previousDepartment.DepartmentName,
                'previousPosition': decreeInfo.previousPosition.positionTitle
            }

        }]

        return JsonResponse({'transferInfo': transfer_info})

    if decreeInstance.decreeType == 'Присвоение звания':

        decreeInfo = RankUpInfo.objects.get(decreeId=decreeInstance)

        rank_up_info = [{
            'decreeInfo': {
                'decreeId': decreeInstance.id,
                'decreeType': decreeInstance.decreeType,
                'decreeNumber': decreeInstance.decreeNumber,
                'decreeDate': decreeInstance.decreeDate,
                'person': person_data,
            },
            'newRank': decreeInfo.newRank.rankTitle,
            'previousRank': decreeInfo.previousRank.rankTitle

        }]

        return JsonResponse({'rankUpInfo': rank_up_info})


@csrf_exempt
def decreeConfirmation(request):
    if request.method == 'POST':
        # 1 L 2 K 3 O 4 P/D
        data = json.loads(request.body.decode('utf-8'))
        decreeId = data.get('decreeId')

        decree_instance = DecreeList.objects.get(pk=decreeId)
        personInstance = decree_instance.personId

        if decree_instance.decreeType == 'Назначение':
            decreeInfo = AppointmentInfo.objects.get(decreeId=decree_instance)
            decree_instance.isConfirmed = True
            decree_instance.save()

            staffingTableInstance = StaffingTable.objects.get(staffing_table_department=decreeInfo.appointmentDepartment, staffing_table_position=decreeInfo.appointmentPosition)
            Vacancy.delete(staffingTableInstance.vacancy_list.first())
            staffingTableInstance.save()

            response_data = {'status': 'success', 'message': 'Приказ о назначении согласован'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')

        if decree_instance.decreeType == 'Перемещение':

            decreeInfo = TransferInfo.objects.get(decreeId=decree_instance)
            personsPositionInfo = PositionInfo.objects.get(person=personInstance)
            OldStaffingTableInstance = StaffingTable.objects.get(staffing_table_department=personsPositionInfo.department, staffing_table_position=personsPositionInfo.position)
            NewStaffingTableInstance = StaffingTable.objects.get(staffing_table_department=decreeInfo.newDepartment, staffing_table_position=decreeInfo.newPosition)

            Vacancy.delete(NewStaffingTableInstance.vacancy_list.first())
            NewStaffingTableInstance.save()

            personsPositionInfo.department = decreeInfo.newDepartment
            personsPositionInfo.position = decreeInfo.newPosition
            personsPositionInfo.receivedDate = decree_instance.decreeDate
            personsPositionInfo.save()

            Vacancy.objects.create(
                position=OldStaffingTableInstance.staffing_table_position,
                department=OldStaffingTableInstance.staffing_table_department,
                available_date=decree_instance.decreeDate
            )

            decree_instance.isConfirmed = True
            decree_instance.save()

            response_data = {'status': 'success', 'message': 'Приказ о перемещении согласован'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')

        if decree_instance.decreeType == 'Присвоение звания':

            decreeInfo = RankUpInfo.objects.get(decreeId=decree_instance)
            personsRankInfo = RankInfo.objects.get(person=personInstance)

            personsRankInfo.militaryRank = decreeInfo.newRank
            personsRankInfo.receivedDate = decree_instance.decreeDate
            personsRankInfo.save()

            decree_instance.isConfirmed = True
            decree_instance.save()

            response_data = {'status': 'success', 'message': 'Приказ о присвоении звания согласован'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')





class DecreeListViewSet(viewsets.ModelViewSet):
    queryset = DecreeList.objects.all()
    serializer_class = DecreeListSerializer
    permission_classes = (IsAuthenticated,)


class SpecCheckViewSet(viewsets.ModelViewSet):
    queryset = SpecCheck.objects.all()
    serializer_class = SpecCheckSerializer
    permission_classes = (IsAuthenticated,)


class SickLeaveViewSet(viewsets.ModelViewSet):
    queryset = SickLeave.objects.all()
    serializer_class = SickLeaveSerializer
    permission_classes = (IsAuthenticated,)


class InvestigationViewSet(viewsets.ModelViewSet):
    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer
    permission_classes = (IsAuthenticated,)
