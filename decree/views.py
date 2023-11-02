from django.shortcuts import render
from rest_framework import generics, viewsets

from .models import DecreeList, SpecCheck, SickLeave
from .serializers import DecreeListSerializer, SpecCheckSerializer, SickLeaveSerializer


class DecreeListViewSet(viewsets.ModelViewSet):
    queryset = DecreeList.objects.all()
    serializer_class = DecreeListSerializer


class SpecCheckViewSet(viewsets.ModelViewSet):
    queryset = SpecCheck.objects.all()
    serializer_class = SpecCheckSerializer


class SickLeaveViewSet(viewsets.ModelViewSet):
    queryset = SickLeave.objects.all()
    serializer_class = SickLeaveSerializer
