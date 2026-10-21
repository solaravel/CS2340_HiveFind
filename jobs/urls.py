from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('map/', views.job_map, name='jobs.map'),
    path('create/', views.create, name='jobs.create'),
    path('<int:id>/edit/', views.edit, name='jobs.edit'),
    path('', views.index, name='jobs.index'), ## jobs page that isnt map
    path('api/jobs/', views.jobs_api, name='jobs.api'),
    path('search/', views.job_search, name='jobs.search'),
    path('candidates/', views.candidate_search, name='jobs.candidates'),
    path('<int:id>/', views.show, name='jobs.show'), ##pages for individual jobs
    path('<int:id>/application/create/', views.create_application, name='jobs.create_application'),
    path('report/posting/<int:id>/', views.report_posting, name='jobs.report_posting'),
    path('report/user/<int:id>/', views.report_user, name='jobs.report_user'),
]
