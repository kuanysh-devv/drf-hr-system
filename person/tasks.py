import datetime
from celery import shared_task
from django.core.management.base import BaseCommand
from person.models import Vacation, Person
from decree.models import DecreeList, OtpuskInfo, KomandirovkaInfo
from military_rank.models import RankInfo
from working_history.models import WorkingHistory
from datetime import date, datetime, timedelta


@shared_task(bind=True)
def add_vacation_days(self, *args, **kwargs):
    # Get the current year
    current_year = datetime.now().year
    # Check if vacation instances for the current year already exis
    people = Person.objects.filter(isFired=False)

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
        pravo_experience = calculate_experience(working_histories=work_history, type='PravoOhranka')

        if Vacation.objects.filter(year=current_year, personId=person, daysType="Обычные").exists():
            print(f'Basic vacation instances for this year for {person} already exist.')
        else:
            Vacation.objects.create(
                year=current_year,
                daysType="Обычные",
                daysCount=30,  # You can set the initial vacation days count here
                personId=person
            )

        if pravo_experience['years'] >= 10:
            if Vacation.objects.filter(year=current_year, personId=person, daysType="Стажные").exists():
                print(f'Experience vacation instances for this year for {person} already exist.')
            else:
                print(person, pravo_experience['years'])

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


@shared_task
def remove_unnecessary_rank_infos():
    unnecessary_rank_infos = find_unnecessary_rank_infos()
    for rank_info in unnecessary_rank_infos:
        rank_info.delete()


def find_unnecessary_rank_infos():
    # Query all RankInfo instances
    all_rank_infos = RankInfo.objects.all()
    unnecessary_rank_infos = []

    # Iterate through each RankInfo instance
    for rank_info in all_rank_infos:
        # Check if the RankInfo instance is not connected to any Person instance
        if not rank_info.person_set.exists():
            unnecessary_rank_infos.append(rank_info)

    return unnecessary_rank_infos


@shared_task(bind=True)
def check_vacation_komandirovka_status(self, *args, **kwargs):
    today = date.today()
    persons_on_vacation = Person.objects.filter(inVacation=True)
    persons_in_komandirovka = Person.objects.filter(inKomandirovka=True)
    for person in persons_on_vacation:
        decree_info_instance = OtpuskInfo.objects.filter(personId=person, decreeId__decreeType="Отпуск", decreeId__isConfirmed=True).last()
        if decree_info_instance:
            end_date = decree_info_instance.endDate
            if today == end_date + timedelta(days=1):
                person.inVacation = False
                person.save()
                print(f"Сотрудник {person.iin} вышел с отпуска")

    for person in persons_in_komandirovka:
        decree_info_instance = KomandirovkaInfo.objects.filter(personId=person, decreeId__decreeType="Командировка", decreeId__isConfirmed=True).last()
        if decree_info_instance:
            end_date = decree_info_instance.endDate
            if today == end_date + timedelta(days=1):
                person.inKomandirovka = False
                person.save()
                print(f"Сотрудник {person.iin} прибыл из командировки")


