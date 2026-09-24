from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('map/', views.job_map, name='jobs.map'),
    path('', views.index, name='jobs.index'), ## jobs page that isnt map
    path('api/jobs/', views.jobs_api, name='jobs.api'),
]
