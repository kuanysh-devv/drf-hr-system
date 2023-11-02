from rest_framework import serializers

from .models import Position, PositionInfo, WorkingHistory


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class PositionInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PositionInfo
        fields = "__all__"


class WorkingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHistory
        fields = "__all__"

