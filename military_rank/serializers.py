from rest_framework import serializers

from military_rank.models import MilitaryRank, RankInfo


class MilitaryRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilitaryRank
        fields = "__all__"


class RankInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RankInfo
        fields = "__all__"