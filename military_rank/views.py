from rest_framework import viewsets

from .models import MilitaryRank, RankInfo
from .serializers import MilitaryRankSerializer, RankInfoSerializer


class MilitaryRankViewSet(viewsets.ModelViewSet):
    queryset = MilitaryRank.objects.all()
    serializer_class = MilitaryRankSerializer


class RankInfoViewSet(viewsets.ModelViewSet):
    queryset = RankInfo.objects.all()
    serializer_class = RankInfoSerializer
