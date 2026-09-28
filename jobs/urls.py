from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('map/', views.job_map, name='jobs.map'),
    path('create/', views.create, name='jobs.create'),
    path('', views.index, name='jobs.index'), ## jobs page that isnt map
    path('api/jobs/', views.jobs_api, name='jobs.api'),
    path('search/', views.job_search, name='jobs.search'),
    path('<int:id>/', views.show, name='jobs.show'), ##pages for individual jobs
    path('<int:id>/application/create/', views.create_application, name='jobs.create_application'),
]
