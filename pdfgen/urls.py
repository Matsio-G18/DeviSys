from django.urls import path
from . import views

app_name = 'pdfgen'

urlpatterns = [
    path('devis/<int:devis_id>/pdf/', views.generer_devis_pdf, name='devis_pdf'),
]
