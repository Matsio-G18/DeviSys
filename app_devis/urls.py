
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pwa import views as pwa_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('clients/', include('clients.urls')),
    path('devis/', include('devis.urls')),
    path('', include('core.urls')),
    path('pdf/', include('pdfgen.urls')),
    path('manifest.json', pwa_views.manifest, name='manifest'),
    path('sw.js', pwa_views.service_worker, name='service_worker'),
    path('pwa/', pwa_views.install, name='pwa_home'),
    path('install/', pwa_views.install, name='pwa_install'),
]
