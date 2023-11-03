from django import forms
from .models import ResidentInfo


class ResidentInfoForm(forms.ModelForm):
    class Meta:
        model = ResidentInfo
        fields = '__all__'
