from django.contrib import admin

from person.models import Person, Gender, FamilyStatus, Relative, FamilyComposition, ClassCategory, Autobiography, \
    Reward, LanguageSkill, SportSkill

admin.site.register(Person)
admin.site.register(Gender)
admin.site.register(FamilyStatus)
admin.site.register(Relative)
admin.site.register(FamilyComposition)
admin.site.register(ClassCategory)
admin.site.register(Autobiography)
admin.site.register(Reward)
admin.site.register(LanguageSkill)
admin.site.register(SportSkill)

