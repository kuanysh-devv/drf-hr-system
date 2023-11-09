from django.db.models.signals import post_save
from django.dispatch import receiver

from person.models import Person
from position.models import PositionInfo
from .models import WorkingHistory


