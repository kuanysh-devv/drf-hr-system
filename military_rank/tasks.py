from celery import shared_task
from celery.contrib.abortable import AbortableTask
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import RankInfo, MilitaryRank
from decree.models import DecreeList,AppointmentInfo
from time import sleep


@shared_task(bind=True, base=AbortableTask)
def create_rank_info_after_months(self, month_count, appointmentInstanceId):
    # Calculate the receivedDate by adding the specified number of months to today's date

    try:
        appointmentInstance = AppointmentInfo.objects.get(pk=appointmentInstanceId)
    except AppointmentInfo.DoesNotExist:
        return JsonResponse(
            {'error': f'Нету сущности Архива назначении'}, status=400)

    person = appointmentInstance.personId

    received_date = appointmentInstance.decreeId.decreeDate + relativedelta(days=int(month_count) * 30 + 1)
    if appointmentInstance.appointmentType == 'Впервые принятый':
        # Create a dictionary representing the RankInfo instance
        new_rank_info_data = {
            "militaryRank": MilitaryRank.objects.get(rankTitle="Лейтенант"),
            "receivedType": "Очередное",
            "decreeNumber": appointmentInstance.decreeId.decreeNumber,  # Update with the actual decree number
            "receivedDate": received_date.strftime("%Y-%m-%d"),
        }

        createdRankInfo = RankInfo.objects.create(**new_rank_info_data)
        person.rankInfo = createdRankInfo
        person.save()
        return 'Успешно присвоено звание сотруднику'



