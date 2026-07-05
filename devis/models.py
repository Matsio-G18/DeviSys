from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone


class Devis(models.Model):
    TEMPLATE_CHOICES = [
        ('particulier', 'Particulier'),
        ('ong', 'ONG'),
        ('entreprise', 'Entreprise / Grande Structure'),
    ]
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('negociation', 'En Négociation'),
        ('accepte', 'Accepté / Validé'),
        ('refuse', 'Refusé / Annulé'),
    ]
    DEVISE_CHOICES = [
        ('XAF', 'FCFA (XAF)'),
        ('EUR', 'Euro (€)'),
        ('USD', 'Dollar ($)'),
    ]
    
    # 🆕 COMBO POUR LES DOMAINES D'ACTIVITÉ
    DOMAINE_CHOICES = [
        ('general', 'Général / Commerce'),
        ('btp', 'Bâtiment & Travaux Publics (BTP)'),
        ('it', 'Informatique & Télécoms (IT)'),
        ('service', 'Prestation de Services / Conseil'),
    ]

    # --- INFORMATIONS DE BASE ---
    numero = models.CharField(max_length=50, unique=True, editable=False, blank=True, null=True)
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT)
    domaine = models.CharField(max_length=20, choices=DOMAINE_CHOICES, default='general', verbose_name="Domaine d'activité")
    type_template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='entreprise')
    objet = models.CharField(max_length=255, help_text='Ex: Fourniture et installation de serveurs')
    date_emission = models.DateField(auto_now_add=True, blank=True, null=True)
    validite_jours = models.IntegerField(default=30, help_text="Durée de validité de l'offre en jours")
    date_validite = models.DateField(help_text='Calculé automatiquement à la sauvegarde', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')

    # --- CONTEXTE ADMINISTRATIF ET PROJET ---
    reference_appel_offre = models.CharField(max_length=100, blank=True, null=True, help_text="N° de l'Appel d'Offres du client")
    reference_projet = models.CharField(max_length=100, blank=True, null=True, help_text='Nom du projet ou code budgétaire')
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES, default='XAF')

    # --- RÉCAPITULATIF FINANCIER ---
    total_ht = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_ttc = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        verbose_name = "Devis"
        verbose_name_plural = "Devis"

    def __str__(self):
        return self.numero or "Devis sans numéro"

    def generate_numero(self):
        annee_courante = timezone.localdate().strftime('%Y')
        # On inclut le domaine dans le préfixe pour une meilleure organisation (Ex: DEV-BZV-IT-2026)
        prefix = f'DEV-BZV-{self.domaine.upper()}-{annee_courante}'
        
        last = Devis.objects.filter(numero__startswith=prefix).order_by('-numero').first()
        
        if last and last.numero:
            try:
                dernier_index = int(last.numero.split('-')[-1])
                suffix = dernier_index + 1
            except (ValueError, IndexError):
                suffix = 1
        else:
            suffix = 1
            
        return f'{prefix}-{suffix:03d}'

    def update_totals(self):
        lignes = self.lignes.all()
        total_ht = lignes.aggregate(total=Sum('montant_ht'))['total'] or Decimal('0.00')

        total_ttc = Decimal('0.00')
        for ligne in lignes:
            tva_facteur = Decimal('1.00') + (ligne.taux_tva / Decimal('100.00'))
            montant_ttc_ligne = (ligne.montant_ht * tva_facteur).quantize(Decimal('0.01'))
            total_ttc += montant_ttc_ligne

        Devis.objects.filter(pk=self.pk).update(
            total_ht=total_ht.quantize(Decimal('0.01')),
            total_ttc=total_ttc.quantize(Decimal('0.01'))
        )

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generate_numero()
            
        if not self.date_emission:
            self.date_emission = timezone.localdate()
            
        self.date_validite = self.date_emission + timedelta(days=self.validite_jours)
        super().save(*args, **kwargs)


class LigneDevis(models.Model):
    # Toutes les unités regroupées. Elles seront filtrées dynamiquement dans l'interface ou l'API.
    UNITE_CHOICES = [
        # --- Général ---
        ('U', 'Unité (U)'),
        ('ENS', 'Ensemble (ENS)'),
        ('FF', 'Forfait (FF)'),
        
        # --- BTP ---
        ('M', 'Mètre (m)'),
        ('M2', 'Mètre carré (m²)'),
        ('M3', 'Mètre cube (m³)'),
        ('KG', 'Kilogramme (kg)'),
        ('L', 'Litre (L)'),
        ('TONNE', 'Tonne (T)'),
        
        # --- IT & Services ---
        ('H', 'Heure (H)'),
        ('J', 'Jour (J)'),
        ('MOIS', 'Mois (M)'),
        ('CJ', 'Configuration / Jour'),
    ]

    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='lignes')
    designation = models.CharField(max_length=255, help_text='Nom du produit ou du service')
    description = models.TextField(blank=True, null=True, help_text='Détails ou spécifications techniques supplémentaires')
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES, default='U', help_text='Unité de mesure')
    
    qte = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    pu_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix Unitaire HT")
    remise_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text='Remise en % sur cette ligne')
    
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'), editable=False)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))

    class Meta:
        verbose_name = "Ligne de devis"
        verbose_name_plural = "Lignes de devis"

    def __str__(self):
        return f"{self.designation} ({self.unite})"

    def save(self, *args, **kwargs):
        brut_ht = (self.qte or Decimal('0.00')) * (self.pu_ht or Decimal('0.00'))
        
        if self.remise_pourcentage > 0:
            reduction = brut_ht * (self.remise_pourcentage / Decimal('100.00'))
            self.montant_ht = brut_ht - reduction
        else:
            self.montant_ht = brut_ht
            
        self.montant_ht = self.montant_ht.quantize(Decimal('0.01'))
        super().save(*args, **kwargs)


@receiver(post_save, sender=LigneDevis)
@receiver(post_delete, sender=LigneDevis)
def update_devis_totals_on_line_change(sender, instance, **kwargs):
    instance.devis.update_totals()
