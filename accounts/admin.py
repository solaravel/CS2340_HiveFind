from django.contrib import admin
from .models import JobSeeker, Skill

#Register
admin.site.register(JobSeeker)
admin.site.register(Skill)