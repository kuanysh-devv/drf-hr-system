from django.contrib import admin

from decree.models import DecreeList, SpecCheck, SickLeave, Investigation

admin.site.register(DecreeList)
admin.site.register(SpecCheck)
admin.site.register(SickLeave)
admin.site.register(Investigation)
