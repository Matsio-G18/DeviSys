from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.db.models import F, Sum
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

    # --- INFORMATIONS DE BASE ---
    numero = models.CharField(max_length=50, unique=True, editable=False, blank=True, null=True)
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT)
    type_template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='entreprise')
    objet = models.CharField(max_length=255, help_text='Ex: Fourniture et installation de serveurs')
    date_emission = models.DateField(auto_now_add=True, blank=True, null=True)
    validite_jours = models.IntegerField(default=30, help_text='Durée de validité de l\'offre en jours')
    date_validite = models.DateField(help_text='Calculé automatiquement à la sauvegarde', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')

    # --- CONTEXTE ADMINISTRATIF ET PROJET ---
    reference_appel_offre = models.CharField(max_length=100, blank=True, null=True, help_text='N° de l\'Appel d\'Offres du client')
    reference_projet = models.CharField(max_length=100, blank=True, null=True, help_text='Nom du projet ou code budgétaire')
    devise = models.CharField(max_length=3, choices=DEVISE_CHOICES, default='XAF')

    # --- RÉCAPITULATIF FINANCIER ---
    total_ht = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    total_ttc = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return self.numero

    def generate_numero(self):
        # 1. Récupère l'année en cours automatiquement (Ex: 2026)
        annee_courante = timezone.localdate().strftime('%Y')
        prefix = f'DEV-BZV-{annee_courante}'
        
        # 2. Cherche le dernier devis créé cette année qui commence par ce préfixe
        last = Devis.objects.filter(numero__startswith=prefix).order_by('-numero').first()
        
        if last and last.numero.startswith(prefix):
            try:
                # Récupère les 3 derniers chiffres (ex: '001' devient 1)
                dernier_index = int(last.numero.split('-')[-1])
                suffix = dernier_index + 1
            except (ValueError, IndexError):
                suffix = 1
        else:
            # Si aucun devis n'existe pour cette année, on commence à 1
            suffix = 1
            
        return f'{prefix}-{suffix:03d}'

    def update_totals(self):
        # Calcule la somme de tous les montants HT des lignes de ce devis
        totals = self.lignes.aggregate(
            total_ht=Sum('montant_ht')
        )
        self.total_ht = totals['total_ht'] or Decimal('0.00')

        # Calcule le total TTC en appliquant la TVA de chaque ligne
        total_ttc = Decimal('0.00')
        for ligne in self.lignes.all():
            total_ttc += ligne.montant_ht * (Decimal('1.00') + (ligne.taux_tva or Decimal('0.00')) / Decimal('100.00'))

        self.total_ttc = total_ttc.quantize(Decimal('0.01'))
        self.save(update_fields=['total_ht', 'total_ttc'])
        return self.total_ht, self.total_ttc

    def save(self, *args, **kwargs):
        # Génère le numéro unique automatiquement juste avant l'enregistrement en base
        if not self.numero:
            self.numero = self.generate_numero()
            
        if not self.date_emission:
            self.date_emission = timezone.localdate()
            
        self.date_validite = self.date_emission + timedelta(days=self.validite_jours)
        super().save(*args, **kwargs)


class LigneDevis(models.Model):
    # Les unités courantes pour le commerce, le bâtiment et l'informatique
    UNITE_CHOICES = [
        ('U', 'Unité (U)'),
        ('ENS', 'Ensemble (ENS)'),
        ('FF', 'Forfait (FF)'),
        ('H', 'Heure (H)'),
        ('J', 'Jour (J)'),
        ('M', 'Mètre (m)'),
        ('M2', 'Mètre carré (m²)'),
        ('M3', 'Mètre cube (m³)'),
        ('KG', 'Kilogramme (kg)'),
        ('L', 'Litre (L)'),
        ('CJ', 'Configuration / Jour'),
    ]

    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='lignes')
    
    # --- DESCRIPTION DE LIGNE ---
    designation = models.CharField(max_length=255, help_text='Nom du produit ou du service')
    description = models.TextField(blank=True, null=True, help_text='Détails ou spécifications techniques supplémentaires')
    unite = models.CharField(max_length=10, choices=UNITE_CHOICES, default='U', help_text='Unité de mesure')
    
    # --- QUANTITÉ ET PRIX ---
    qte = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Quantité")
    pu_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prix Unitaire HT")
    remise_pourcentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), help_text='Remise en % sur cette ligne')
    
    # --- CALCULS AUTOMATIQUES ---
    montant_ht = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'), editable=False)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('18.00'))

    class Meta:
        verbose_name = "Ligne de devis"
        verbose_name_plural = "Lignes de devis"

    def __str__(self):
        return f"{self.designation} ({self.unite})"

    def save(self, *args, **kwargs):
        # 1. Calcul du montant brut
        brut_ht = (self.qte or Decimal('0.00')) * (self.pu_ht or Decimal('0.00'))
        
        # 2. Application de la remise si elle existe
        if self.remise_pourcentage > 0:
            reduction = brut_ht * (self.remise_pourcentage / Decimal('100.00'))
            self.montant_ht = brut_ht - reduction
        else:
            self.montant_ht = brut_ht
            
        self.montant_ht = self.montant_ht.quantize(Decimal('0.01'))
        
        # 3. Sauvegarde de la ligne
        super().save(*args, **kwargs)
        
        # 4. Mise à jour automatique des totaux du devis lié
        self.devis.update_totals()
