from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Position, PositionInfo, WorkingHistory
from .serializers import PositionSerializer, PositionInfoSerializer, WorkingHistorySerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (IsAuthenticated,)


class PositionInfoViewSet(viewsets.ModelViewSet):
    queryset = PositionInfo.objects.all()
    serializer_class = PositionInfoSerializer
    permission_classes = (IsAuthenticated,)


class WorkingHistoryViewSet(viewsets.ModelViewSet):
    queryset = WorkingHistory.objects.all()
    serializer_class = WorkingHistorySerializer
    permission_classes = (IsAuthenticated,)
