from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import BirthInfo
from .serializers import BirthInfoSerializer


class BirthInfoViewSet(viewsets.ModelViewSet):
    queryset = BirthInfo.objects.all()
    serializer_class = BirthInfoSerializer
    permission_classes = (IsAuthenticated,)

