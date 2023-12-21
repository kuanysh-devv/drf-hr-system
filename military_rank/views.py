from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Check if 'militaryRank' is present in the request data
        if 'militaryRank' in request.data:
            military_rank_id = request.data['militaryRank']

            # Check if the military rank with the given ID exists
            try:
                military_rank = MilitaryRank.objects.get(rankTitle=military_rank_id)
            except MilitaryRank.DoesNotExist:
                return Response({"detail": "Military Rank not found"}, status=status.HTTP_400_BAD_REQUEST)

            # Update the 'militaryRank' field
            instance.militaryRank = military_rank
            instance.save()

        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Update the instance with the provided data
        instance.__dict__.update(serializer.validated_data)
        instance.save()
        return Response(serializer.data)
