from rest_framework import serializers

from .models import BirthInfo


class BirthInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = BirthInfo
        fields = "__all__"

