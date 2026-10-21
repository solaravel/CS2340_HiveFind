from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import JobSeeker


class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [('seeker', 'Job Seeker'), ('recruiter', 'Recruiter')]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, initial='seeker', widget=forms.RadioSelect, label='I am a',
    )

    class Meta(UserCreationForm.Meta):
        model = User


class JobSeekerForm(forms.ModelForm):
    new_skills = forms.CharField(
        required=False,
        label='Add new skills',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Python, Java'}),
        help_text='Separate multiple skills with commas'
    )
    class Meta:
        model = JobSeeker
        fields = ['name', 'headline', 'skills', 'education', 'work_exp', 'links',
                  'is_public', 'latitude', 'longitude']
        widgets = {'skills': forms.CheckboxSelectMultiple(),}
        labels = {
            'work_exp': 'Work Experience',
            'is_public': 'Make my profile visible to recruiters',
            'latitude': 'Latitude (for the applicant map)',
            'longitude': 'Longitude (for the applicant map)',
        }
