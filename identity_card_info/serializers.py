from rest_framework import serializers

from .models import IdentityCardInfo


class IdentityCardInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdentityCardInfo
        fields = "__all__"

