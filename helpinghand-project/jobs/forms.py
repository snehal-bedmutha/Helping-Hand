from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import job



class Jobform(forms.ModelForm):
    class Meta:
        model = job
        fields = ['job_name', 'job_description','job_type','skills_needed', 'hourly_pay']
