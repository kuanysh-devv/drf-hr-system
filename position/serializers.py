from rest_framework import serializers

from location.serializers import DepartmentSerializer
from military_rank.serializers import MilitaryRankSerializer
from .models import Position, PositionInfo


class PositionSerializer(serializers.ModelSerializer):
    maxRank = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = "__all__"

    @staticmethod
    def get_maxRank(obj):
        maxRank = obj.maxRank
        if maxRank:
            return MilitaryRankSerializer(maxRank).data
        return None


class PositionInfoSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    class Meta:
        model = PositionInfo
        fields = "__all__"

    @staticmethod
    def get_position(obj):
        position = obj.position
        if position:
            return PositionSerializer(position).data
        return None

    @staticmethod
    def get_department(obj):
        department = obj.department
        if department:
            return DepartmentSerializer(department).data
        return None
