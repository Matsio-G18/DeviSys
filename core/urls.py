from django.urls import path
from . import views
from pwa import views as pwa_views  # Importe les vues de votre app PWA

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Routes indispensables pour la détection PWA
    path('manifest.json', pwa_views.manifest, name='pwa_manifest'),
    path('sw.js', pwa_views.service_worker, name='pwa_sw'),
    path('installer/', pwa_views.install, name='pwa_install'),
]
