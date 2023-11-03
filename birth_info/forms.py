from django import forms
from .models import BirthInfo


class BirthInfoForm(forms.ModelForm):
    class Meta:
        model = BirthInfo
        fields = '__all__'
