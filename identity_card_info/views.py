from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import IdentityCardInfo
from .serializers import IdentityCardInfoSerializer


class IdentityCardInfoViewSet(viewsets.ModelViewSet):
    queryset = IdentityCardInfo.objects.all()
    serializer_class = IdentityCardInfoSerializer
    permission_classes = (IsAuthenticated,)

