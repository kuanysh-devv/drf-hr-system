from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from location.models import Department
from person.models import Person
from person.serializers import PersonSerializer
from .models import Position, PositionInfo
from .serializers import PositionSerializer, PositionInfoSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated,)


class PositionInfoViewSet(viewsets.ModelViewSet):
    queryset = PositionInfo.objects.all()
    serializer_class = PositionInfoSerializer
    permission_classes = (IsAuthenticated,)


@csrf_exempt
def positions_by_department(request, department_id):
    try:
        department = Department.objects.get(pk=department_id)
        positions_info = PositionInfo.objects.filter(department=department)
        position_ids = positions_info.values('position').distinct()
        # Get unique Position models based on the obtained IDs
        unique_positions = Position.objects.filter(id__in=position_ids)

        # Serialize positions and include related persons
        serialized_positions = []
        for position in unique_positions:
            position_data = PositionSerializer(position).data
            persons = Person.objects.filter(positionInfo__position=position)
            person_data = [{'id': person.id, 'surname': person.surname, 'firstName': person.firstName, 'patronymic': person.patronymic,
                            'photo': person.photo_set.first().photoBinary} for person in persons]
            position_data['persons'] = person_data
            serialized_positions.append(position_data)

        return JsonResponse({'positions': serialized_positions})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)


