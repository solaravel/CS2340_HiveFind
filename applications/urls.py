from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='applications.index'),
    path('<int:id>/apply', views.apply, name='applications.apply'),
]
