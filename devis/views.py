from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView
from django.db import transaction
import io
from django.conf import settings
from decimal import Decimal
from django.http import FileResponse
from django.urls import reverse
from .models import Devis
from .forms import DevisForm, LigneFormSet

from .utils import envoyer_notifications_devis, build_devis_pdf_bytes

from django.contrib import messages
from django.core.mail import EmailMessage

class DevisListView(ListView):
    model = Devis
    template_name = 'devis/devis_list.html'
    context_object_name = 'devis_list'


class DevisDetailView(DetailView):
    model = Devis
    template_name = 'devis/devis_detail.html'
    context_object_name = 'devis'


def _save_devis_and_formset(form, formset, instance=None):
    devis = form.save(commit=False)
    devis.save()

    lignes = formset.save(commit=False)
    for ligne in lignes:
        ligne.devis = devis
        ligne.save()

    for ligne in formset.deleted_objects:
        ligne.delete()

    devis.update_totals()
    devis.save()
    return devis


@transaction.atomic
def devis_create(request):
    if request.method == 'POST':
        form = DevisForm(request.POST)
        formset = LigneFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            devis = _save_devis_and_formset(form, formset)
            return redirect(reverse('devis:detail', args=[devis.pk]))
    else:
        form = DevisForm()
        formset = LigneFormSet()
    return render(request, 'devis/devis_form.html', {'form': form, 'formset': formset, 'is_update': False})


@transaction.atomic
def devis_update(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    if request.method == 'POST':
        form = DevisForm(request.POST, instance=devis)
        formset = LigneFormSet(request.POST, instance=devis)
        if form.is_valid() and formset.is_valid():
            devis = _save_devis_and_formset(form, formset, instance=devis)
            return redirect(reverse('devis:detail', args=[devis.pk]))
    else:
        form = DevisForm(instance=devis)
        formset = LigneFormSet(instance=devis)
    return render(request, 'devis/devis_form.html', {'form': form, 'formset': formset, 'is_update': True, 'devis': devis})


@transaction.atomic
def devis_delete(request, pk):
    devis = get_object_or_404(Devis, pk=pk)
    if request.method == 'POST':
        devis.delete()
        return redirect(reverse('devis:list'))
    return render(request, 'devis/devis_confirm_delete.html', {'devis': devis})




def telecharger_devis_pdf(request, devis_id):
    devis = get_object_or_404(Devis, pk=devis_id)
    pdf_data = build_devis_pdf_bytes(devis)
    return FileResponse(io.BytesIO(pdf_data), as_attachment=True, filename=f"Devis_{devis.numero}.pdf")


def envoyer_devis_par_email(request, devis_id):
    devis = get_object_or_404(Devis, pk=devis_id)
    client = devis.client

    # Vérification de sécurité : le client doit avoir un e-mail valide
    if not client.email:
        messages.error(request, f"❌ Impossible d'envoyer : Le client '{client.nom}' n'a pas d'adresse e-mail enregistrée.")
        return redirect(request.META.get('HTTP_REFERER', '/admin/'))

    try:
        # 2. Personnalisation du message selon le type de template (Particulier, ONG, Entreprise)
        if devis.type_template == 'particulier':
            salutation = f"Bonjour {client.nom},"
            corps_texte = f"Veuillez trouver ci-joint votre devis concernant votre projet : \"{devis.objet}\"."
            formule_fin = "Nous restons à votre disposition pour toute question. À très bientôt !"
            
        elif devis.type_template == 'ong':
            salutation = f"À l'attention de l'équipe de {client.nom},"
            corps_texte = f"Dans le cadre de nos échanges, nous avons le plaisir de vous transmettre notre proposition budgétaire pour l'action : \"{devis.objet}\"."
            formule_fin = "Espérant que cette proposition réponde à vos critères d'impact, nous restons disponibles pour échanger."
            
        else: # Entreprise / Grande Structure
            salutation = f"Mesdames, Messieurs les responsables de {client.nom},"
            corps_texte = f"Suite à l'étude de votre cahier des charges, vous trouverez ci-joint notre offre commerciale et technique pour le projet : \"{devis.objet}\"."
            formule_fin = "Nous nous tenons à votre entière disposition pour caler une réunion technique de cadrage si nécessaire."

        # Assemblage final du corps du texte de l'e-mail
        message_complet = f"""{salutation}

{corps_texte}

Référence du document : {devis.numero}
Durée de validité de l'offre : {devis.validite_jours} jours

{formule_fin}

Cordialement,
L'équipe Don & Gloire
"""

        sujet = f"Proposition Commerciale Don & Gloire : {devis.numero}"


        email = EmailMessage(
            subject=sujet,
            body=message_complet,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[client.email],
        )

        # 2. Génération du PDF ReportLab en mémoire
        pdf_data = build_devis_pdf_bytes(devis)

        # 3. Attacher le PDF à l'e-mail
        nom_fichier = f"Devis_{devis.numero}.pdf"
        email.attach(nom_fichier, pdf_data, 'application/pdf')

        # 4. Envoi de l'e-mail
        email.send()

        # 5. Mise à jour du statut du devis
        if devis.statut == 'brouillon':
            devis.statut = 'envoye'
            devis.save(update_fields=['statut'])

        messages.success(request, f"🚀 Le devis {devis.numero} a été envoyé avec succès à l'adresse {client.email} !")

    except Exception as e:
        messages.error(request, f"💥 Une erreur est survenue lors de l'envoi : {str(e)}")

    return redirect(request.META.get('HTTP_REFERER', '/admin/'))

