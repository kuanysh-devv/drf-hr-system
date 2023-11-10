from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from location.models import Location, Department
from location.serializers import LocationSerializer, DepartmentSerializer
from person.models import Person
from person.serializers import PersonSerializer
from position.models import Position, PositionInfo
from position.serializers import PositionSerializer, PositionInfoSerializer
from staffing_table.models import StaffingTable
from staffing_table.serializers import StaffingTableSerializer


class StaffingTableViewSet(viewsets.ModelViewSet):
    queryset = StaffingTable.objects.all()
    serializer_class = StaffingTableSerializer
    permission_classes = (IsAuthenticated,)


def getStaffingTable(request, *args, **kwargs):
    location_id = request.GET.get('location_id')

    try:
        location = Location.objects.get(pk=location_id)

        departments = Department.objects.filter(Location=location)
        depSerializer = DepartmentSerializer(departments, many=True)
        data = {'Departments': []}
        for department in departments:
            DistinctPositionInfosToGetPositions = PositionInfo.objects.filter(department=department).distinct(
                'position')
            # GlavExpertDc
            # ExpertDC
            positionList = []
            for posinfo in DistinctPositionInfosToGetPositions:
                position_data = PositionSerializer(posinfo.position).data
                currentPositionInfos = PositionInfo.objects.filter(position=posinfo.position)
                personsOnPosition = Person.objects.filter(positionInfo__in=currentPositionInfos)
                position_data['persons'] = PersonSerializer(personsOnPosition, many=True).data

                staffing_table_entry = StaffingTable.objects.filter(
                    position=posinfo.position,
                    department=department
                ).first()

                if staffing_table_entry:
                    available_slots = staffing_table_entry.max_count - staffing_table_entry.current_count
                    position_data['available_slots'] = available_slots
                positionList.append(position_data)
            print(positionList)

            departamentSerialized = DepartmentSerializer(department).data
            departamentSerialized['positionList'] = positionList
            data['Departments'].append(departamentSerialized)

        return JsonResponse(data)

    except Location.DoesNotExist:
        return JsonResponse({'error': 'Location not found'}, status=404)
