from rest_framework import serializers

from .models import SpecCheck, SickLeave, DecreeList


class DecreeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = DecreeList
        fields = "__all__"


class SpecCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecCheck
        fields = "__all__"


class SickLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = SickLeave
        fields = "__all__"