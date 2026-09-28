from django import forms

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'company', 'description', 'address', 'city', 'state',
            'latitude', 'longitude', 'salary_min', 'salary_max', 'is_remote',
            'visa_sponsorship', 'skills',
        ]
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}