from datetime import datetime, timedelta

from rest_framework import serializers

from working_history.models import WorkingHistory


class WorkingHistorySerializer(serializers.ModelSerializer):
    overall_experience = serializers.SerializerMethodField()
    pravo_experience = serializers.SerializerMethodField()

    class Meta:
        model = WorkingHistory
        fields = "__all__"

    def get_related_working_histories(self, instance):
        person_id = instance.personId
        working_history_objects = WorkingHistory.objects.filter(personId=person_id)
        return working_history_objects

    def get_overall_experience(self, instance):
        working_history_objects = self.get_related_working_histories(instance)
        overall_experience = self.calculate_experience(working_histories=working_history_objects, type='All')
        return overall_experience

    def get_pravo_experience(self, instance):
        working_history_objects = self.get_related_working_histories(instance)
        pravo_experience = self.calculate_experience(working_histories=working_history_objects,
                                                     type='PravoOhranka')
        return pravo_experience

    def to_representation(self, instance):
        data = super().to_representation(instance)

        overall_experience = self.get_overall_experience(instance)
        pravo_experience = self.get_pravo_experience(instance)

        # Remove the 'overall_experience' and 'pravo_experience' keys from each working history item
        for key in ['overall_experience', 'pravo_experience']:
            data.pop(key, None)

        # Add 'overall_experience' and 'pravo_experience' only once at the top level
        if not hasattr(self, 'added_experience'):
            data['overall_experience'] = overall_experience
            data['pravo_experience'] = pravo_experience
            self.added_experience = True

        return data

    @staticmethod
    def calculate_experience(working_histories, type):
        total_experience = timedelta()

        if type == 'All':
            for working_history in working_histories:
                start_date = working_history.startDate
                end_date = working_history.endDate or datetime.now().date()
                experience = end_date - start_date
                total_experience += experience

        if type == 'PravoOhranka':
            for working_history in working_histories:
                if working_history.isPravoOhranka:
                    start_date = working_history.startDate
                    end_date = working_history.endDate or datetime.now().date()
                    experience = end_date - start_date
                    if working_history.HaveCoefficient:
                        experience = experience * 1.5
                    total_experience += experience

        total_years = total_experience.days // 365
        remaining_days = total_experience.days % 365
        total_months = remaining_days // 30
        remaining_days %= 30

        overall_experience = {
            'years': total_years,
            'months': total_months,
            'days': remaining_days
        }

        return overall_experience
