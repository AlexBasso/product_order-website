from django import forms
from django.forms import ModelForm

from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=32)
    last_name = forms.CharField(max_length=32)
    class Meta:
        model = Profile
        fields = ['avatar']
