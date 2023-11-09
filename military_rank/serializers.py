from rest_framework import serializers

from military_rank.models import MilitaryRank, RankInfo


class MilitaryRankSerializer(serializers.ModelSerializer):
    class Meta:
        model = MilitaryRank
        fields = "__all__"


class RankInfoSerializer(serializers.ModelSerializer):
    militaryRank = serializers.SerializerMethodField()

    class Meta:
        model = RankInfo
        fields = "__all__"

    @staticmethod
    def get_militaryRank(obj):
        militaryRank = obj.militaryRank
        if militaryRank:
            return MilitaryRankSerializer(militaryRank).data
        return None