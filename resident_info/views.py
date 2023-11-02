from rest_framework import viewsets

from .models import ResidentInfo
from .serializers import ResidentInfoSerializer


class ResidentInfoViewSet(viewsets.ModelViewSet):
    queryset = ResidentInfo.objects.all()
    serializer_class = ResidentInfoSerializer

