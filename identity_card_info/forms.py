from django import forms
from .models import IdentityCardInfo


class IdentityCardInfoForm(forms.ModelForm):
    class Meta:
        model = IdentityCardInfo
        fields = '__all__'
