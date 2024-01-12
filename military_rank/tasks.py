from celery import shared_task
from celery.contrib.abortable import AbortableTask
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from .models import RankInfo, MilitaryRank
from decree.models import DecreeList,AppointmentInfo
from time import sleep


@shared_task(bind=True, base=AbortableTask)
def create_rank_info_after_months(self, month_count, decreenumber):
    # Calculate the receivedDate by adding the specified number of months to today's date
    received_date = datetime.now() + relativedelta(minutes=int(month_count))
    decreeInstance = None

    try:
        decreeInstance = DecreeList.objects.get(decreeNumber=decreenumber)
    except DecreeList.DoesNotExist:
        # Handle the case when the object is not found
        person = None
        print("No DecreeList found for decreeNumber: {decreenumber}")

    decreeInfo = AppointmentInfo.objects.get(decreeId=decreeInstance)
    person = decreeInstance.personId

    if decreeInfo.appointmentType == 'Впервые принятый':
        # Create a dictionary representing the RankInfo instance
        new_rank_info_data = {
            "militaryRank": MilitaryRank.objects.get(rankTitle="Лейтенант"),
            "receivedType": "Внеочередное",
            "decreeNumber": decreenumber,  # Update with the actual decree number
            "receivedDate": received_date.strftime("%Y-%m-%d"),
        }

        createdRankInfo = RankInfo.objects.create(**new_rank_info_data)
        person.rankInfo = createdRankInfo
        person.save()
        return 'Успешно присвоено звание сотруднику'



