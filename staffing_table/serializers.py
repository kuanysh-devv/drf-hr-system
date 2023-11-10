from rest_framework import serializers

from .models import StaffingTable


class StaffingTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffingTable
        fields = "__all__"
