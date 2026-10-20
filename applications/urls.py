from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='applications.index'),
    path('pipeline/', views.pipeline, name='applications.pipeline'),
    path('<int:id>/apply', views.apply, name='applications.apply'),
    path('<int:id>/status/', views.update_status, name='applications.update_status'),
    path('<int:id>/', views.view_app, name='applications.view_app'),
]
