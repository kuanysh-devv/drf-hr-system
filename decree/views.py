import json
from dotenv import load_dotenv
import os
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from staffing_table.models import StaffingTable, Vacancy
from location.models import Department
from military_rank.models import MilitaryRank, RankInfo
from person.models import RankArchive, Vacation
from photo.models import Photo
from position.models import PositionInfo, Position
from position.serializers import PositionSerializer, PositionInfoSerializer
from working_history.models import WorkingHistory
from .models import DecreeList, SpecCheck, SickLeave, Investigation, TransferInfo, RankUpInfo, AppointmentInfo, \
    OtpuskInfo, KomandirovkaInfo
from .serializers import DecreeListSerializer, SpecCheckSerializer, SickLeaveSerializer, InvestigationSerializer
from minio import Minio
from rest_framework.decorators import action

load_dotenv()

MINIO_ENDPOINT = os.getenv('MINIO_ENDPOINT')
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY')
MINIO_SECURE = os.getenv('MINIO_SECURE') == 'True'
MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME')


class DecreeListViewSet(viewsets.ModelViewSet):
    queryset = DecreeList.objects.all()
    serializer_class = DecreeListSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=False, methods=['get'])
    def getDecreeList(self, request, *args, **kwargs):
        decrees = DecreeList.objects.all()

        # Serialize the decree data
        decree_data = []
        for decree in decrees:
            decree_info = {
                'decreeId': decree.id,
                'decreeType': decree.decreeType,
                'decreeNumber': decree.decreeNumber,
                'decreeDate': decree.decreeDate,
                'decreeIsConfirmed': decree.isConfirmed,
                'persons': [],  # Placeholder for person data
            }

            # Retrieve person data for each person in personIds
            for person in decree.personIds.all():
                try:
                    persons_rank_info = person.rankInfo
                    rank_title = persons_rank_info.militaryRank.rankTitle if persons_rank_info else ''
                except RankInfo.DoesNotExist:
                    rank_title = ''

                person_data = {
                    'iin': person.iin,
                    'pin': person.pin,
                    'surname': person.surname,
                    'firstName': person.firstName,
                    'patronymic': person.patronymic,
                    'positionInfo': person.positionInfo.position.positionTitle,
                    'rankInfo': rank_title,
                }

                # Get the photo for the person
                photo = Photo.objects.filter(personId=person).first()
                if photo:
                    person_data['photo'] = photo.photoBinary
                else:
                    person_data['photo'] = None

                decree_info['persons'].append(person_data)

            decree_data.append(decree_info)

        return JsonResponse({'decrees': decree_data})

    @action(detail=False, methods=['get'])
    def getDecreeInfo(self, request, *args, **kwargs):
        decreeId = request.GET.get('decreeId')

        try:
            decreeInstance = DecreeList.objects.get(pk=decreeId)
        except DecreeList.DoesNotExist:
            return JsonResponse({'error': 'Decree not found'})
        persons = []
        for person in decreeInstance.personIds.all():
            try:
                personsRankInfo = person.rankInfo
            except RankInfo.DoesNotExist:
                personsRankInfo = None

        # Check if personsRankInfo is not None before accessing its attributes
            rank_title = personsRankInfo.militaryRank.rankTitle if personsRankInfo else ''

            person_data = {
                'iin': person.iin,
                'pin': person.pin,
                'surname': person.surname,
                'firstName': person.firstName,
                'patronymic': person.patronymic,
                'positionInfo': PositionInfoSerializer(person.positionInfo).data,
                'rankInfo': rank_title,  # Use the rank_title variable
            }

        # Get the photo for the person
            photo = Photo.objects.filter(personId=person).first()
            if photo:
                person_data['photo'] = photo.photoBinary
            else:
                person_data['photo'] = None

            persons.append(person_data)

        if decreeInstance.decreeType == 'Назначение':
            decreeInfo = AppointmentInfo.objects.get(decreeId=decreeInstance)

            appointmentInfo = [{
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'document': decreeInstance.minioDocName,
                    'person': persons,
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
                    'document': decreeInstance.minioDocName,
                    'person': persons,
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
                    'document': decreeInstance.minioDocName,
                    'person': persons,
                },
                'newRank': decreeInfo.newRank.rankTitle,
                'previousRank': decreeInfo.previousRank.rankTitle

            }]

            return JsonResponse({'rankUpInfo': rank_up_info})
        if decreeInstance.decreeType == 'Увольнение':
            firing_info = {
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'document': decreeInstance.minioDocName,
                    'person': persons,
                },
            }

            return JsonResponse({'firingInfo': firing_info})

        if decreeInstance.decreeType == 'Отпуск':
            decreeInfo = OtpuskInfo.objects.get(decreeId=decreeInstance)

            otpusk_info = [{
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'document': decreeInstance.minioDocName,
                    'person': persons,
                },
                'startDate': decreeInfo.startDate,
                'endDate': decreeInfo.endDate,
                'otpuskType': decreeInfo.otpuskType,
                'benefitChoice': decreeInfo.benefitChoice,
                'oldBasicDaysCount': decreeInfo.oldBasicDaysCount,
                'oldExperienceDaysCount': decreeInfo.oldExperiencedDaysCount,
                'newBasicDaysCount': decreeInfo.newBasicDaysCount,
                'newExperienceDaysCount': decreeInfo.newExperiencedDaysCount,
            }]

            return JsonResponse({'otpuskInfo': otpusk_info})

        if decreeInstance.decreeType == 'Командировка':
            decreeInfo = KomandirovkaInfo.objects.get(decreeId=decreeInstance)

            komandirovka_info = [{
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'document': decreeInstance.minioDocName,
                    'person': persons,
                },
                'startDate': decreeInfo.startDate,
                'endDate': decreeInfo.endDate,
                'otpuskType': decreeInfo.otpuskType,
                'benefitChoice': decreeInfo.benefitChoice,
                'oldBasicDaysCount': decreeInfo.oldBasicDaysCount,
                'oldExperienceDaysCount': decreeInfo.oldExperiencedDaysCount,
                'newBasicDaysCount': decreeInfo.newBasicDaysCount,
                'newExperienceDaysCount': decreeInfo.newExperiencedDaysCount,
            }]

            return JsonResponse({'otpuskInfo': otpusk_info})

    @action(detail=False, methods=['post'])
    def decreeConfirmation(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        decreeId = data.get('decreeId')

        decree_instance = DecreeList.objects.get(pk=decreeId)
        persons = decree_instance.personIds.all()
        for personInstance in persons:
            if decree_instance.decreeType == 'Назначение':
                decreeInfo = AppointmentInfo.objects.get(decreeId=decree_instance)
                decree_instance.isConfirmed = True
                decree_instance.save()

                staffingTableInstance = StaffingTable.objects.get(
                    staffing_table_department=decreeInfo.appointmentDepartment,
                    staffing_table_position=decreeInfo.appointmentPosition)

                Vacancy.delete(staffingTableInstance.vacancy_list.first())
                staffingTableInstance.save()

                Vacation.objects.create(
                    personId=personInstance,
                    year=decree_instance.decreeDate.year,
                    daysCount=0
                )

                response_data = {'status': 'success', 'message': 'Приказ о назначении согласован'}
                response_json = json.dumps(response_data)
                return HttpResponse(response_json, content_type='application/json')

            if decree_instance.decreeType == 'Перемещение':
                decreeInfo = TransferInfo.objects.get(decreeId=decree_instance)
                personsPositionInfo = PositionInfo.objects.get(person=personInstance)
                OldStaffingTableInstance = StaffingTable.objects.get(
                    staffing_table_department=personsPositionInfo.department,
                    staffing_table_position=personsPositionInfo.position)
                NewStaffingTableInstance = StaffingTable.objects.get(staffing_table_department=decreeInfo.newDepartment,
                                                                     staffing_table_position=decreeInfo.newPosition)

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

            if decree_instance.decreeType == 'Увольнение':

                personInstance.isFired = True
                personInstance.save()

                try:
                    vacation = Vacation.objects.get(personId=personInstance, year=decree_instance.decreeDate.year)
                    vacation.daysCount = 0
                    vacation.save()

                except Vacation.DoesNotExist:
                    return JsonResponse({'error': 'У сотрудника не имеется объект отпускных дней'},
                                        status=400)

                decree_instance.isConfirmed = True
                decree_instance.save()

                response_data = {'status': 'success', 'message': 'Приказ об увольнении согласован'}
                response_json = json.dumps(response_data)
                return HttpResponse(response_json, content_type='application/json')

            if decree_instance.decreeType == 'Отпуск':

                decreeInfo = OtpuskInfo.objects.get(decreeId=decree_instance)
                if decreeInfo.otpuskType == 'Отпуск':
                    personsBasicVacation = Vacation.objects.get(personId=personInstance, year=decreeInfo.startDate.year,
                                                                daysType="Обычные")
                    if decreeInfo.oldExperiencedDaysCount:
                        personsExperiencedVacation = Vacation.objects.get(personId=personInstance,
                                                                          year=decreeInfo.startDate.year,
                                                                          daysType="Стажные")
                        personsExperiencedVacation.daysCount = decreeInfo.newExperiencedDaysCount
                        personsExperiencedVacation.save()

                    personsBasicVacation.daysCount = decreeInfo.newBasicDaysCount
                    personsBasicVacation.save()

                    personInstance.inVacation = True
                    personInstance.save()
                    decree_instance.isConfirmed = True
                    decree_instance.save()

                    response_data = {'status': 'success', 'message': 'Приказ об отпуске согласован'}
                    response_json = json.dumps(response_data)
                    return HttpResponse(response_json, content_type='application/json')

                if decreeInfo.otpuskType == 'Отпуск Кратко':
                    personInstance.inVacation = True
                    personInstance.save()
                    decree_instance.isConfirmed = True
                    decree_instance.save()

                    response_data = {'status': 'success', 'message': 'Приказ об отпуске согласован'}
                    response_json = json.dumps(response_data)
                    return HttpResponse(response_json, content_type='application/json')

            if decree_instance.decreeType == 'Командировка':
                personInstance.inKomandirovka = True
                personInstance.save()
                decree_instance.isConfirmed = True
                decree_instance.save()

                response_data = {'status': 'success', 'message': 'Приказ о командировке согласован'}
                response_json = json.dumps(response_data)
                return HttpResponse(response_json, content_type='application/json')

    @action(detail=False, methods=['get'])
    def decreeDownload(self, request, *args, **kwargs):
        decreeId = request.GET.get('decreeId')

        decree_instance = DecreeList.objects.get(pk=decreeId)

        minio_client = Minio(MINIO_ENDPOINT,
                             access_key=MINIO_ACCESS_KEY,
                             secret_key=MINIO_SECRET_KEY,
                             secure=False)
        document_data = minio_client.get_object(MINIO_BUCKET_NAME, decree_instance.minioDocName)
        document = document_data.read()

        # Serve document for download
        response = HttpResponse(document,
                                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        response['Content-Disposition'] = 'attachment; filename={decree_instance.minioDocName}'
        return response


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
