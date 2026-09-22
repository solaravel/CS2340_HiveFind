from django.urls import path

from . import views

urlpatterns = [
    path('map/', views.job_map, name='jobs.map'),
    path('api/jobs/', views.jobs_api, name='jobs.api'),
]
