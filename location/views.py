from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Location, Department
from .serializers import LocationSerializer, DepartmentSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (IsAuthenticated,)


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (IsAuthenticated,)


@csrf_exempt
def departments_by_location(request, location_name):
    try:
        location = Location.objects.get(LocationName=location_name)
        departments = Department.objects.filter(Location=location)

        serializer = DepartmentSerializer(departments, many=True)

        return JsonResponse({'departments': serializer.data})
    except Department.DoesNotExist:
        return JsonResponse({'error': 'Location not found'}, status=404)