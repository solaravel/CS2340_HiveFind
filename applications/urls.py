from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='applications.index'),
    path('pipeline/', views.pipeline, name='applications.pipeline'),
    path('map/applicants/', views.applicant_map, name='applications.applicant_map'),
    path('map/applicants/data/', views.applicant_map_data, name='applications.applicant_map_data'),
    path('<int:id>/apply', views.apply, name='applications.apply'),
    path('<int:id>/status/', views.update_status, name='applications.update_status'),
    path('<int:id>/', views.view_app, name='applications.view_app'),
    path('<int:id>/email/', views.email_candidate, name='applications.email_candidate'),
]
