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
from person.serializers import PersonSerializer
from photo.models import Photo
from position.models import PositionInfo, Position
from position.serializers import PositionSerializer, PositionInfoSerializer
from working_history.models import WorkingHistory
from .models import DecreeList, SpecCheck, SickLeave, Investigation, TransferInfo, RankUpInfo, AppointmentInfo, \
    OtpuskInfo, KomandirovkaInfo, FiringInfo
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
                'bases': [base.baseName for base in decree.decreeBases.all()],
                'decreeIsConfirmed': decree.isConfirmed,
                'forms': [],
            }
            # Retrieve person data for each person in personIds
            if decree.decreeType == "Назначение":
                appointment_infos = AppointmentInfo.objects.filter(decreeId=decree)
                for appointment_info in appointment_infos:
                    person_data = PersonSerializer(appointment_info.personId).data
                    appointment_data = {
                        'person': person_data,
                        'newDepartment': appointment_info.appointmentDepartment.DepartmentName,
                        'newPosition': appointment_info.appointmentPosition.positionTitle,
                        'probationMonthCount': appointment_info.appointmentProbation,
                        'appointmentType': appointment_info.appointmentType,
                    }
                    decree_info['forms'].append(appointment_data)

            if decree.decreeType == "Перемещение":
                transfer_infos = TransferInfo.objects.filter(decreeId=decree)
                for transfer_info in transfer_infos:
                    person_data = PersonSerializer(transfer_info.personId).data
                    transfer_data = {
                        'person': person_data,
                        'newPosition': {
                            'newDepartment': transfer_info.newDepartment.DepartmentName,
                            'newPosition': transfer_info.newPosition.positionTitle
                        },
                        'previousPosition': {
                            'previousDepartment': transfer_info.previousDepartment.DepartmentName,
                            'previousPosition': transfer_info.previousPosition.positionTitle
                        }
                    }
                    decree_info['forms'].append(transfer_data)

            if decree.decreeType == "Присвоение звания":
                rankup_infos = RankUpInfo.objects.filter(decreeId=decree)
                for rankup_info in rankup_infos:
                    person_data = PersonSerializer(rankup_info.personId).data
                    rankup_data = {
                        'person': person_data,
                        'newRank': rankup_info.newRank.rankTitle,
                        'previousRank': rankup_info.previousRank.rankTitle,
                        'receivedType': rankup_info.receivedType,
                        'receivedDate': rankup_info.receivedDate
                    }
                    decree_info['forms'].append(rankup_data)

            if decree.decreeType == "Увольнение":
                firing_infos = FiringInfo.objects.filter(decreeId=decree)
                for firing_info in firing_infos:
                    person_data = PersonSerializer(firing_info.personId).data
                    firing_data = {
                        'person': person_data,
                        'firingDate': firing_info.firingDate,
                    }
                    decree_info['forms'].append(firing_data)

            if decree.decreeType == "Командировка":
                komandirovka_infos = KomandirovkaInfo.objects.filter(decreeId=decree)
                for komandirovka_info in komandirovka_infos:
                    person_data = PersonSerializer(komandirovka_info.personId).data
                    komandirovka_data = {
                        'person': person_data,
                        'startDate': komandirovka_info.startDate,
                        'endDate': komandirovka_info.endDate,
                        'departure': komandirovka_info.departure,
                        'travelChoice': komandirovka_info.travelChoice,
                        'transport': komandirovka_info.transport
                    }
                    decree_info['forms'].append(komandirovka_data)

            decree_data.append(decree_info)

        return JsonResponse({'decrees': decree_data})

    @action(detail=False, methods=['get'])
    def getDecreeInfo(self, request, *args, **kwargs):
        decreeId = request.GET.get('decreeId')

        try:
            decreeInstance = DecreeList.objects.get(pk=decreeId)
        except DecreeList.DoesNotExist:
            return JsonResponse({'error': 'Decree not found'})
        if decreeInstance.decreeType == 'Назначение':
            forms = []
            appointment_infos = AppointmentInfo.objects.filter(decreeId=decreeInstance)
            for appointmentInfo in appointment_infos:
                person_data = PersonSerializer(appointmentInfo.personId).data

                person_data = {
                    'person': person_data,
                    'newDepartment': appointmentInfo.appointmentDepartment.DepartmentName,
                    'newPosition': appointmentInfo.appointmentPosition.positionTitle,
                    'probationMonthCount': appointmentInfo.appointmentProbation,
                    'appointmentType': appointmentInfo.appointmentType,
                }

                forms.append(person_data)

            appointmentInfo = {
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'document': decreeInstance.minioDocName,
                    'bases': [base.baseName for base in decreeInstance.decreeBases.all()],
                    'forms': forms,
                }
            }

            return JsonResponse({'appointmentInfo': appointmentInfo})

        if decreeInstance.decreeType == 'Перемещение':
            forms = []
            transfer_infos = TransferInfo.objects.filter(decreeId=decreeInstance)
            for transferInfo in transfer_infos:
                person_data = PersonSerializer(transferInfo.personId).data

                person_data = {
                    'person': person_data,
                    'newPosition': {
                        'newDepartment': transferInfo.newDepartment.DepartmentName,
                        'newPosition': transferInfo.newPosition.positionTitle
                    },
                    'previousPosition': {
                        'previousDepartment': transferInfo.previousDepartment.DepartmentName,
                        'previousPosition': transferInfo.previousPosition.positionTitle
                    }
                }
                forms.append(person_data)

            transfer_info = {
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'document': decreeInstance.minioDocName,
                    'bases': [base.baseName for base in decreeInstance.decreeBases.all()],
                    'forms': forms,
                }
            }

            return JsonResponse({'transferInfo': transfer_info})

        if decreeInstance.decreeType == 'Присвоение звания':
            forms = []
            rankup_infos = RankUpInfo.objects.filter(decreeId=decreeInstance)
            for rankupInfo in rankup_infos:
                person_data = PersonSerializer(rankupInfo.personId).data

                person_data = {
                    'person': person_data,
                    'newRank': rankupInfo.newRank.rankTitle,
                    'previousRank': rankupInfo.previousRank.rankTitle,
                    'receivedType': rankupInfo.receivedType,
                    'receivedDate': rankupInfo.receivedDate
                }
                forms.append(person_data)

            rank_up_info = {
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'bases': [base.baseName for base in decreeInstance.decreeBases.all()],
                    'document': decreeInstance.minioDocName,
                    'forms': forms,
                }
            }

            return JsonResponse({'rankUpInfo': rank_up_info})
        if decreeInstance.decreeType == 'Увольнение':
            forms = []
            firing_infos = FiringInfo.objects.filter(decreeId=decreeInstance)
            for firingInfo in firing_infos:
                person_data = PersonSerializer(firingInfo.personId).data

                person_data = {
                    'person': person_data,
                    'firingDate': firingInfo.firingDate,
                }
                forms.append(person_data)

            firing_info = {
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'bases': [base.baseName for base in decreeInstance.decreeBases.all()],
                    'document': decreeInstance.minioDocName,
                    'forms': forms,
                }
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
                'otzivDate': decreeInfo.otzivDate,
                'oldBasicDaysCount': decreeInfo.oldBasicDaysCount,
                'oldExperienceDaysCount': decreeInfo.oldExperiencedDaysCount,
                'newBasicDaysCount': decreeInfo.newBasicDaysCount,
                'newExperienceDaysCount': decreeInfo.newExperiencedDaysCount,
            }]

            return JsonResponse({'otpuskInfo': otpusk_info})

        if decreeInstance.decreeType == 'Командировка':
            forms = []
            komandirovka_infos = KomandirovkaInfo.objects.filter(decreeId=decreeInstance)
            for komandirovka_info in komandirovka_infos:
                person_data = PersonSerializer(komandirovka_info.personId).data

                person_data = {
                    'person': person_data,
                    'startDate': komandirovka_info.startDate,
                    'endDate': komandirovka_info.endDate,
                    'departure': komandirovka_info.departure,
                    'travelChoice': komandirovka_info.travelChoice,
                    'transport': komandirovka_info.transport
                }
                forms.append(person_data)
            komandirovka_info = {
                'decreeInfo': {
                    'decreeId': decreeInstance.id,
                    'decreeType': decreeInstance.decreeType,
                    'decreeNumber': decreeInstance.decreeNumber,
                    'decreeDate': decreeInstance.decreeDate,
                    'bases': [base.baseName for base in decreeInstance.decreeBases.all()],
                    'document': decreeInstance.minioDocName,
                    'forms': forms,
                }
            }

            return JsonResponse({'komandirovka_info': komandirovka_info})

    @action(detail=False, methods=['post'])
    def decreeConfirmation(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        decreeId = data.get('decreeId')

        decree_instance = DecreeList.objects.get(pk=decreeId)
        if decree_instance.decreeType == 'Назначение':

            appointment_infos = AppointmentInfo.objects.filter(decreeId=decree_instance)
            for appointmentInfo in appointment_infos:
                staffingTableInstance = StaffingTable.objects.get(
                    staffing_table_department=appointmentInfo.appointmentDepartment,
                    staffing_table_position=appointmentInfo.appointmentPosition)

                Vacancy.delete(staffingTableInstance.vacancy_list.first())
                staffingTableInstance.save()

            decree_instance.isConfirmed = True
            decree_instance.save()

            response_data = {'status': 'success', 'message': 'Приказ о назначении согласован'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')
        if decree_instance.decreeType == 'Перемещение':

            transfer_infos = TransferInfo.objects.filter(decreeId=decree_instance)
            for transferInfo in transfer_infos:
                print(transfer_infos)
                personsPositionInfo = PositionInfo.objects.get(person=transferInfo.personId)
                print(personsPositionInfo)
                OldStaffingTableInstance = StaffingTable.objects.get(
                    staffing_table_department=personsPositionInfo.department,
                    staffing_table_position=personsPositionInfo.position)
                NewStaffingTableInstance = StaffingTable.objects.get(
                    staffing_table_department=transferInfo.newDepartment,
                    staffing_table_position=transferInfo.newPosition)
                print("Old: ", OldStaffingTableInstance)
                print("New: ", NewStaffingTableInstance)
                Vacancy.delete(NewStaffingTableInstance.vacancy_list.first())
                NewStaffingTableInstance.save()

                personsPositionInfo.department = transferInfo.newDepartment
                personsPositionInfo.position = transferInfo.newPosition
                personsPositionInfo.receivedDate = decree_instance.decreeDate
                personsPositionInfo.save()
                print(personsPositionInfo)
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
            rankupinfos = RankUpInfo.objects.filter(decreeId=decree_instance)
            for rankupinfo in rankupinfos:
                personsRankInfo = RankInfo.objects.get(person=rankupinfo.personId)

                personsRankInfo.militaryRank = rankupinfo.newRank
                personsRankInfo.receivedDate = rankupinfo.receivedDate
                personsRankInfo.save()

            decree_instance.isConfirmed = True
            decree_instance.save()
            response_data = {'status': 'success', 'message': 'Приказ о присвоении звания согласован'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')

        if decree_instance.decreeType == 'Увольнение':
            firing_infos = FiringInfo.objects.filter(decreeId=decree_instance)
            for firing_info in firing_infos:
                firing_info.personId.isFired = True
                firing_info.personId.save()

                try:
                    basicVacation = None
                    expVacation = None
                    try:
                        basicVacation = Vacation.objects.get(personId=firing_info.personId, daysType="Обычные")
                    except Vacation.DoesNotExist:
                        pass

                    try:
                        expVacation = Vacation.objects.get(personId=firing_info.personId, daysType="Стажные")
                    except Vacation.DoesNotExist:
                        pass

                    if basicVacation:
                        basicVacation.delete()
                    if expVacation:
                        expVacation.delete()

                except Vacation.DoesNotExist:
                    pass

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
            if decreeInfo.otpuskType == 'Отпуск Отзыв':
                personsBasicVacation = Vacation.objects.get(personId=personInstance, year=decreeInfo.startDate.year,
                                                            daysType="Обычные")
                personsBasicVacation.daysCount = decreeInfo.newBasicDaysCount
                personsBasicVacation.save()

                personInstance.inVacation = False
                personInstance.save()
                decree_instance.isConfirmed = True
                decree_instance.save()

                response_data = {'status': 'success', 'message': 'Приказ об отзыве отпуска согласован'}
                response_json = json.dumps(response_data)
                return HttpResponse(response_json, content_type='application/json')

        if decree_instance.decreeType == 'Командировка':
            komandirovka_infos = KomandirovkaInfo.objects.filter(decreeId=decree_instance)
            for komandirovka_info in komandirovka_infos:
                personInstance = komandirovka_info.personId
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
