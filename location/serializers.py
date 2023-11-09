from rest_framework import serializers

from .models import Department, Location


class DepartmentSerializer(serializers.ModelSerializer):
    Location = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = "__all__"

    @staticmethod
    def get_Location(obj):
        LocationIns = obj.Location
        if LocationIns:
            return LocationSerializer(LocationIns).data
        return None


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
