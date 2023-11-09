from rest_framework import serializers

from working_history.models import WorkingHistory


class WorkingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingHistory
        fields = "__all__"
