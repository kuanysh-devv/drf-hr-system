from datetime import timedelta, datetime

from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from working_history.models import WorkingHistory
from working_history.serializers import WorkingHistorySerializer


# Create your views here.
class WorkingHistoryViewSet(viewsets.ModelViewSet):
    queryset = WorkingHistory.objects.all()
    serializer_class = WorkingHistorySerializer
    permission_classes = (IsAuthenticated,)
