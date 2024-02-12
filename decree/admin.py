from django.contrib import admin

from decree.models import DecreeList, SpecCheck, SickLeave, Investigation, RankUpInfo, AppointmentInfo, TransferInfo, OtpuskInfo, KomandirovkaInfo

admin.site.register(DecreeList)
admin.site.register(SpecCheck)
admin.site.register(SickLeave)
admin.site.register(Investigation)
admin.site.register(RankUpInfo)
admin.site.register(TransferInfo)
admin.site.register(AppointmentInfo)
admin.site.register(OtpuskInfo)
admin.site.register(KomandirovkaInfo)

