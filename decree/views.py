from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import DecreeList, SpecCheck, SickLeave
from .serializers import DecreeListSerializer, SpecCheckSerializer, SickLeaveSerializer


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
