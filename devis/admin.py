from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Devis, LigneDevis

admin.site.site_header = "Application Devis"

class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 1
    fields = ['designation', 'description', 'unite', 'qte', 'pu_ht', 'remise_pourcentage', 'taux_tva', 'montant_ht', 'ordre']
    readonly_fields = ['montant_ht']
    ordering = ['ordre']



@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    # Remplacement de 'statut' par 'statut_badge' dans la liste
    list_display = ['numero', 'client', 'objet', 'statut', 'total_ht', 'total_ttc', 'bouton_pdf']
    list_filter = ['statut', 'type_template', 'devise']
    search_fields = ['numero', 'client__id', 'objet'] 
    readonly_fields = ['numero', 'total_ht', 'total_ttc', 'date_validite']

    
    fieldsets = [
        ('Informations Générales', {
            'fields': ['numero', 'client', 'type_template', 'objet', 'statut']
        }),
        ('Administration & Projet', {
            'fields': ['reference_appel_offre', 'reference_projet', 'devise', 'validite_jours', 'date_validite']
        }),
        ('Finances', {
            'fields': ['total_ht', 'total_ttc']
        }),
    ]

    # 1. BOUTON PDF EN UN CLIC
    def bouton_pdf(self, obj):
        url = reverse('devis:telecharger_pdf', args=[obj.pk])
        # URL pour l'envoi par e-mail
        url_email = reverse('devis:envoyer_email', args=[obj.pk])
        
        return format_html(
            '<a class="btn btn-xs btn-info" href="{}" target="_blank">'
            '<i class="fas fa-file-pdf"></i> PDF'
            '</a>',
            '<i class="fas fa-paper-plane"></i> Envoyer par Mail</a>',
            url,url_email
        )
    bouton_pdf.short_description = 'Actions disponibles'