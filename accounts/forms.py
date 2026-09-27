from django import forms

from .models import JobSeeker


class JobSeekerForm(forms.ModelForm):
    new_skills = forms.CharField(
        required=False,
        label='Add new skills',
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Python, Java'}),
        help_text='Separate multiple skills with commas'
    )
    class Meta:
        model = JobSeeker
        fields = ['name', 'headline', 'skills', 'education', 'work_exp', 'links']
        widgets = {'skills': forms.CheckboxSelectMultiple(),}
        labels = {'work_exp': 'Work Experience',}
