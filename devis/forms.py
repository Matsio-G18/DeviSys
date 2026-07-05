from django import forms
from django.forms import inlineformset_factory
from .models import Devis, LigneDevis


class DevisForm(forms.ModelForm):
    class Meta:
        model = Devis
        fields = [
            'domaine',  # 🆕 Ajout du combo pour le domaine d'activité
            'client',
            'type_template',
            'objet',
            'validite_jours',
            'statut',
            'reference_appel_offre',
            'reference_projet',
            'devise',
        ]
        widgets = {
            'domaine': forms.Select(attrs={'class': 'form-select'}), # Style combo standard
            'objet': forms.TextInput(attrs={'placeholder': 'Ex: Fourniture et installation de serveurs'}),
            'validite_jours': forms.NumberInput(attrs={'min': 1}),
            'reference_appel_offre': forms.TextInput(attrs={'placeholder': "N° de l'AO Client (Optionnel)"}),
            'reference_projet': forms.TextInput(attrs={'placeholder': 'Nom du projet ou code budget (Optionnel)'}),
        }


class LigneDevisForm(forms.ModelForm):
    class Meta:
        model = LigneDevis
        fields = [
            'designation', 
            'description', 
            'unite', 
            'qte', 
            'pu_ht', 
            'taux_tva', 
            'remise_pourcentage'
        ]
        widgets = {
            'designation': forms.TextInput(attrs={'placeholder': 'Nom du produit ou service'}),
            'description': forms.Textarea(attrs={
                'placeholder': 'Détails ou spécifications techniques (Optionnel)',
                'rows': 1,
            }),
            'qte': forms.NumberInput(attrs={'step': '0.01', 'min': '0.00'}),
            'pu_ht': forms.NumberInput(attrs={'step': '0.01', 'min': '0.00'}),
            'taux_tva': forms.NumberInput(attrs={'step': '0.01', 'min': '0.00'}),
            'remise_pourcentage': forms.NumberInput(attrs={'step': '0.01', 'min': '0.00', 'max': '100.00'}),
        }


LigneFormSet = inlineformset_factory(
    Devis, 
    LigneDevis, 
    form=LigneDevisForm, 
    extra=1,
    can_delete=True
)
