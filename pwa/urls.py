from django.urls import path
from . import views

app_name = 'pwa'

urlpatterns = [
    path('manifest.json', views.manifest, name='manifest'),
    path('sw.js', views.service_worker, name='service_worker'),
    path('install/', views.install, name='install'),
]
