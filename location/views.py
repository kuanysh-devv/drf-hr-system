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
