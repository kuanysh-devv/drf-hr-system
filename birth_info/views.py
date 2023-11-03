from rest_framework import viewsets

from .models import BirthInfo
from .serializers import BirthInfoSerializer


class BirthInfoViewSet(viewsets.ModelViewSet):
    queryset = BirthInfo.objects.all()
    serializer_class = BirthInfoSerializer

