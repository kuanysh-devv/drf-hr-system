import datetime
from celery import shared_task
from django.core.management.base import BaseCommand
from person.models import Vacation, Person
from working_history.models import WorkingHistory
from datetime import timedelta


@shared_task(bind=True)
def add_vacation_days(self, *args, **kwargs):
    # Get the current year
    current_year = datetime.datetime.now().year
    # Check if vacation instances for the current year already exist
    if Vacation.objects.filter(year=current_year).exists():
        print('Vacation instances for this year already exist.')
    else:
        # Create vacation instances for every person
        people = Person.objects.all()

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

        for person in people:
            work_history = WorkingHistory.objects.filter(personId=person).order_by('startDate')

            pravo_experience = calculate_experience(working_histories=work_history,
                                                    type='PravoOhranka')

            Vacation.objects.create(
                year=current_year,
                daysType="Обычные",
                daysCount=30,  # You can set the initial vacation days count here
                personId=person
            )

            if 10 <= pravo_experience['years'] < 15:
                Vacation.objects.create(
                    year=current_year,
                    daysType="Стажные",
                    daysCount=5,
                    personId=person
                )
            if 15 <= pravo_experience['years'] < 20:
                Vacation.objects.create(
                    year=current_year,
                    daysType="Стажные",
                    daysCount=10,
                    personId=person
                )
            if pravo_experience['years'] >= 20:
                Vacation.objects.create(
                    year=current_year,
                    daysType="Стажные",
                    daysCount=15,
                    personId=person
                )
        print('Vacation instances for {} created successfully.'.format(current_year))
