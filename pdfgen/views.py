from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from devis.models import Devis
from devis.utils import build_devis_pdf_bytes
from reportlab.lib.pagesizes import A4

@login_required
def generer_devis_pdf(request, devis_id):
    try:
        devis = get_object_or_404(Devis, pk=devis_id)
        pdf_data = build_devis_pdf_bytes(devis, pagesize=A4)
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Devis_{devis.numero}.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f"Erreur lors de la génération du PDF : {str(e)}", status=500)
