# django_celery/celery.py

import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SPDV2.settings")
app = Celery("SPDV2")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.beat_schedule = {
    'create_vacation': {
        'task': 'person.tasks.add_vacation_days',
        'schedule': crontab(hour='0', minute='0', day_of_month='1', month_of_year='1'),  # Run on the 1st day of January every year
    },
}


app.autodiscover_tasks()
