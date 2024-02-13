# django_celery/celery.py
from __future__ import absolute_import, unicode_literals

import os
from datetime import datetime
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SPDV2.settings")
app = Celery("SPDV2")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.enable_utc = False
app.conf.timezone = 'Asia/Almaty'
app.conf.beat_schedule = {
    'create_vacation': {
        'task': 'person.tasks.add_vacation_days',
        'schedule': crontab(hour='10', minute='0', day_of_month='3', month_of_year='1'),  # Run on the 1st day of January every year
    },
    'remove_unnecessary_rank_infos_monthly': {
        'task': 'person.tasks.remove_unnecessary_rank_infos',
        'schedule': crontab(hour='10', minute='0', day_of_month='1'),  # Run at midnight on the 1st day of every month
    },
    'check_vacation_komandirovka_status': {
        'task': 'person.tasks.check_vacation_komandirovka_status',
        'schedule': crontab(hour='10', minute='0'),
    },
}

app.autodiscover_tasks()
