from django import forms

from .models import JobSeeker


class JobSeekerForm(forms.ModelForm):
    class Meta:
        model = JobSeeker
        fields = ['name', 'headline', 'skills', 'education']
