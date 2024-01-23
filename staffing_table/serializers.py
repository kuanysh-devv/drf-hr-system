from rest_framework import serializers

from .models import StaffingTable, Vacancy


class StaffingTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffingTable
        fields = "__all__"


class VacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = Vacancy
        fields = "__all__"
