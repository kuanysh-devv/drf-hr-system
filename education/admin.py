from django.contrib import admin

from education.models import Education, Course, Attestation, AcademicDegree

admin.site.register(Education)
admin.site.register(Course)
admin.site.register(Attestation)
admin.site.register(AcademicDegree)
