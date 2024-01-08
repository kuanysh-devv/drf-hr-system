import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from location.models import Department
from military_rank.models import MilitaryRank, RankInfo
from person.models import RankArchive
from photo.models import Photo
from position.models import PositionInfo, Position
from working_history.models import WorkingHistory
from .models import DecreeList, SpecCheck, SickLeave, Investigation
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
            'decreeSubType': decree.decreeSubType,
            'decreeDate': decree.decreeDate,
            'person': person_data,
        })

    return JsonResponse({'decrees': decree_data})


def getTransferInfo(request):
    decreeId = request.GET.get('decreeId')

    try:
        personInstance = DecreeList.objects.get(pk=decreeId).personId
    except DecreeList.DoesNotExist:
        return JsonResponse({'error': 'Decree not found'})

    # Get the last two records from WorkingHistory
    working_history_records = WorkingHistory.objects.filter(personId=personInstance).order_by('-id')[:2]

    new_work = working_history_records[0]
    previous_work = working_history_records[1]

    transfer_info = [{
        'newPosition': {
            'newDepartment': new_work.department,
            'newPosition': new_work.positionName
        },
        'previousPosition': {
            'previousDepartment': previous_work.department,
            'previousPosition': previous_work.positionName
        }

    }]

    return JsonResponse({'transferInfo': transfer_info})


@csrf_exempt
def cancelTransfer(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            decreeId = data.get('decreeId')

            # Attempt to get the DecreeList and personInstance
            decree_instance = DecreeList.objects.get(pk=decreeId)
            personInstance = decree_instance.personId

            # Get the last two records from WorkingHistory
            working_history_records = WorkingHistory.objects.filter(personId=personInstance).order_by('-id')[:2]

            new_work = working_history_records[0]
            previous_work = working_history_records[1]

            previous_work.endDate = None
            previous_work.save()

            previousPosition = Position.objects.get(positionTitle=previous_work.positionName)
            previousDepartment = Department.objects.get(DepartmentName=previous_work.department)

            positionInfoInstance = PositionInfo.objects.get(person=personInstance)
            positionInfoInstance.position = previousPosition
            positionInfoInstance.department = previousDepartment
            positionInfoInstance.receivedDate = previous_work.startDate
            positionInfoInstance.save()

            new_work.delete()

            working_history_duplicate = WorkingHistory.objects.filter(personId=personInstance).order_by('-id').first()
            working_history_duplicate.delete()

            decree_instance.delete()

            response_data = {'status': 'success', 'message': 'Transfer canceled successfully'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')

        except DecreeList.DoesNotExist:
            return JsonResponse({'error': 'Decree not found'})

        except Position.DoesNotExist:
            return JsonResponse({'error': 'Position not found'})

        except Department.DoesNotExist:
            return JsonResponse({'error': 'Department not found'})

        except WorkingHistory.DoesNotExist:
            return JsonResponse({'error': 'Working history not found'})

        except Exception as e:
            # Handle other exceptions as needed
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    else:
        # Handling other HTTP methods (e.g., GET, PUT, etc.) if needed
        return HttpResponse("Method not allowed", status=405)


def getRankUpInfo(request):
    decreeId = request.GET.get('decreeId')

    try:
        personInstance = DecreeList.objects.get(pk=decreeId).personId
    except DecreeList.DoesNotExist:
        return JsonResponse({'error': 'Decree not found'})

    # Get the last two records from WorkingHistory
    rank_archive_records = RankArchive.objects.filter(personId=personInstance).order_by('-id')[:2]

    new_rank = rank_archive_records[0]
    previous_rank = rank_archive_records[1]

    transfer_info = [{
        'newRank': new_rank.militaryRank.rankTitle,
        'previousRank': previous_rank.militaryRank.rankTitle

    }]

    return JsonResponse({'rankUpInfo': transfer_info})


@csrf_exempt
def cancelRankUp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            decreeId = data.get('decreeId')

            # Attempt to get the DecreeList and personInstance
            decree_instance = DecreeList.objects.get(pk=decreeId)
            personInstance = decree_instance.personId

            # Get the last two records from WorkingHistory
            rank_archive_records = RankArchive.objects.filter(personId=personInstance).order_by('-id')[:2]

            new_rank = rank_archive_records[0]
            previous_rank = rank_archive_records[1]

            previous_rank.endDate = None
            previous_rank.save()

            previousRank = MilitaryRank.objects.get(rankTitle=previous_rank.militaryRank.rankTitle)

            rankInfoInstance = RankInfo.objects.get(person=personInstance)
            rankInfoInstance.militaryRank = previousRank
            rankInfoInstance.receivedDate = previous_rank.startDate
            rankInfoInstance.save()

            new_rank.delete()

            rank_archive_duplicate = RankArchive.objects.filter(personId=personInstance).order_by('-id').first()
            rank_archive_duplicate.delete()

            decree_instance.delete()

            response_data = {'status': 'success', 'message': 'RankUp canceled successfully'}
            response_json = json.dumps(response_data)
            return HttpResponse(response_json, content_type='application/json')

        except DecreeList.DoesNotExist:
            return JsonResponse({'error': 'Decree not found'})

        except RankInfo.DoesNotExist:
            return JsonResponse({'error': 'RankInfo not found'})

        except MilitaryRank.DoesNotExist:
            return JsonResponse({'error': 'MilitaryRank not found'})

        except RankArchive.DoesNotExist:
            return JsonResponse({'error': 'RankArchive not found'})

        except Exception as e:
            # Handle other exceptions as needed
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    else:
        # Handling other HTTP methods (e.g., GET, PUT, etc.) if needed
        return HttpResponse("Method not allowed", status=405)


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
