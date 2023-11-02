from rest_framework import viewsets

from .models import Position, PositionInfo, WorkingHistory
from .serializers import PositionSerializer, PositionInfoSerializer, WorkingHistorySerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class PositionInfoViewSet(viewsets.ModelViewSet):
    queryset = PositionInfo.objects.all()
    serializer_class = PositionInfoSerializer


class WorkingHistoryViewSet(viewsets.ModelViewSet):
    queryset = WorkingHistory.objects.all()
    serializer_class = WorkingHistorySerializer
