from django.contrib import admin

from decree.models import DecreeList, SpecCheck, SickLeave

admin.site.register(DecreeList)
admin.site.register(SpecCheck)
admin.site.register(SickLeave)
