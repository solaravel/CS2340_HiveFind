from django.shortcuts import render
from .models import JobSeeker
# Create your views here.
def signup():
    pass
def login():
    pass
def view_profile(request, id):
    profile = JobSeeker.objects.get(id=id)
    template_data = {}
    template_data['title'] = profile.name
    template_data['headline'] = profile.headline
    template_data['skills'] = profile.skills
    template_data['education'] = profile.education
    return render(request, 'accounts/view_profile.html', {'template_data': template_data})