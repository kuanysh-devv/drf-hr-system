from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import MilitaryRank, RankInfo
from .serializers import MilitaryRankSerializer, RankInfoSerializer


class MilitaryRankViewSet(viewsets.ModelViewSet):
    queryset = MilitaryRank.objects.all()
    serializer_class = MilitaryRankSerializer
    permission_classes = (IsAuthenticated,)


class RankInfoViewSet(viewsets.ModelViewSet):
    queryset = RankInfo.objects.all()
    serializer_class = RankInfoSerializer
    permission_classes = (IsAuthenticated,)
