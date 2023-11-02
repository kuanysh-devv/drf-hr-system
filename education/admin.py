from django.contrib import admin

from education.models import Education, Course, Attestation

admin.site.register(Education)
admin.site.register(Course)
admin.site.register(Attestation)
