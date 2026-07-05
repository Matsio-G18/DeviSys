from django.db import models
from django.utils import timezone

class Client(models.Model):
    TYPE_CHOICES = [
        ('particulier','Particulier'),
        ('ong','ONG'),
        ('entreprise','Entreprise')
    ]
    code = models.CharField(
        max_length=50, 
        unique=True, 
        editable=False, # Masqué dans l'admin car automatique
        blank=True, 
        null=True
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    nom = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    tel = models.CharField(max_length=50)
    adresse = models.CharField(max_length=200)
    rccm = models.CharField(max_length=100, blank=True, null=True)
    nif = models.CharField(max_length=100, blank=True, null=True)
    agrement_ong = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.get_type_display()})"
    
    def generate_code_client(self):
        # 1. Récupère l'année en cours (Ex: 2026)
        annee_courante = timezone.localdate().strftime('%Y')
        prefix = f'CLT-BZV-{annee_courante}'
        
        # 2. Cherche le dernier client créé cette année avec ce préfixe
        last = Client.objects.filter(code__startswith=prefix).order_by('-code').first()
        
        if last and last.code:
            try:
                # Récupère les 3 derniers chiffres et ajoute 1
                dernier_index = int(last.code.split('-')[-1])
                suffix = dernier_index + 1
            except (ValueError, IndexError):
                suffix = 1
        else:
            suffix = 1
            
        return f'{prefix}-{suffix:03d}'

    