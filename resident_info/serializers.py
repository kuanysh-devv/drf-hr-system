from rest_framework import serializers

from .models import ResidentInfo


class ResidentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidentInfo
        fields = "__all__"
