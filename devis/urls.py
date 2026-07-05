from django.urls import path
from . import views

app_name = 'devis'

urlpatterns = [
    path('', views.DevisListView.as_view(), name='list'),
    path('create/', views.devis_create, name='create'),
    path('<int:pk>/', views.DevisDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.devis_update, name='update'),
    path('<int:pk>/delete/', views.devis_delete, name='delete'),
    path('<int:devis_id>/pdf/', views.telecharger_devis_pdf, name='telecharger_pdf'),
]
