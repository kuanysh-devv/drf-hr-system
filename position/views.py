from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from location.models import Department
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

        serializer = PositionSerializer(unique_positions, many=True)

        return JsonResponse({'positions': serializer.data})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Department not found'}, status=404)


