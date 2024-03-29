from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from location.models import Department
from person.models import Person
from staffing_table.models import StaffingTable, Vacancy
from staffing_table.serializers import VacancySerializer
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

        # Use StaffingTable to get positions in the department
        staffing_info = StaffingTable.objects.filter(staffing_table_department=department)
        serialized_positions = []
        staffing_info = staffing_info.order_by('-staffing_table_position__order')
        for staffing_entry in staffing_info:
            position = staffing_entry.staffing_table_position

            # Create a dictionary with position data
            position_data = PositionSerializer(position).data

            # Calculate available count by subtracting current count from max count
            vacancies = Vacancy.objects.filter(department=department,
                                               position=position)
            position_data['vacancies'] = VacancySerializer(vacancies, many=True).data

            # Get persons for the current position
            persons = Person.objects.filter(positionInfo__position=position, positionInfo__department=department)
            person_data = [{'surname': person.surname, 'firstName': person.firstName, 'patronymic': person.patronymic,
                            'photo': person.photo_set.first().photoBinary} for person in persons]
            position_data['persons'] = person_data

            serialized_positions.append(position_data)

        return JsonResponse({'positions': serialized_positions})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)
