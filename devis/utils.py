from django.core.mail import send_mail
from django.conf import settings
# from twilio.rest import Client
import logging
import io
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger(__name__)

def envoyer_notifications_devis(devis):
    """
    Centralise l'envoi d'e-mail et de SMS au client associé à un devis.
    """
    # Récupération des coordonnées du client
    email_client = getattr(devis.client, 'email', None)
    tel_client = getattr(devis.client, 'tel', None) # Doit être au format international ex: +24206XXX
    
    sujet = f"DeviSys : Votre Devis #{devis.numero}"
    message_texte = (
        f"Bonjour {devis.client.nom},\n\n"
        f"Un nouveau devis concernant l'objet '{devis.objet}' a été émis pour votre structure.\n"
        f"Montant Total TTC : {devis.total_ttc} XAF.\n\n"
        f"Merci pour votre confiance.\n"
        f"L'équipe DeviSys."
    )

    # 1. ENVOI DE L'EMAIL (Si l'adresse est renseignée)
    if email_client:
        try:
            send_mail(
                subject=sujet,
                message=message_texte,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email_client],
                fail_silently=False,
            )
            logger.info(f"E-mail envoyé avec succès à {email_client}")
        except Exception as e:
            logger.error(f"Échec de l'envoi de l'e-mail : {str(e)}")

    # 2. ENVOI DU SMS (Si le numéro est renseigné et configuré)
    # if tel_client and hasattr(settings, 'TWILIO_ACCOUNT_SID'):
    #     try:
    #         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    #         message_sms = client.messages.create(
    #             body=f"DeviSys: Devis #{devis.numero} émis. Montant: {devis.total_ttc} XAF. Merci pour votre confiance.",
    #             from_=settings.TWILIO_PHONE_NUMBER,
    #             to=tel_client
    #         )
    #         logger.info(f"SMS envoyé avec succès à {tel_client}. SID: {message_sms.sid}")
    #     except Exception as e:
    #         logger.error(f"Échec de l'envoi du SMS : {str(e)}")


def build_devis_pdf_bytes(devis, pagesize=letter):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=pagesize, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []

    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    center_bold = ParagraphStyle('CenterBold', parent=styles['Normal'], fontName='Helvetica-Bold', alignment=1)

    header_data = []
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.jpeg')
    if os.path.exists(logo_path):
        logo_img = Image(logo_path, width=130, height=50)
        logo_img.hAlign = 'LEFT'
        header_data.append(logo_img)
    else:
        header_data.append(Paragraph("<b>[Votre Logo]</b>", normal_style))

    infos_text = f"""
    <font size=14 color='#0056b3'><b>DEVIS N° {devis.numero}</b></font><br/><br/>
    <b>Date :</b> {devis.date_emission.strftime('%d/%m/%Y') if devis.date_emission else ''}<br/>
    <b>Objet :</b> {devis.objet}<br/>
    <b>Client :</b> {devis.client}
    """
    header_data.append(Paragraph(infos_text, normal_style))

    header_table = Table([header_data], colWidths=[200, 350])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 25))

    totaux_data = [
        [Paragraph('<b>Total HT</b>', normal_style), f"{devis.total_ht} {devis.devise}"],
        [Paragraph('<b>Total TTC</b>', normal_style), f"{devis.total_ttc} {devis.devise}"]
    ]
    totaux_table = Table(totaux_data, colWidths=[100, 120])
    totaux_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f1f3f5')),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    wrapper_table = Table([['', totaux_table]], colWidths=[330, 220])
    wrapper_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(wrapper_table)
    story.append(Spacer(1, 40))

    signature_data = [
        [
            Paragraph("<b>Pour l'Entreprise</b><br/><font size=8 color='#777'>Bon pour accord</font>", center_bold),
            Paragraph("<b>Pour le Client</b><br/><font size=8 color='#777'>Date, signature et cachet précédés de la mention 'Lu et approuvé'</font>", center_bold)
        ],
        ['', '']
    ]
    signature_table = Table(signature_data, colWidths=[260, 260])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#dddddd')),
        ('HEIGHT', (0,1), (-1,1), 70),
        ('BOX', (0,0), (0,1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (1,0), (1,1), 0.5, colors.HexColor('#cccccc')),
    ]))
    container_signature = Table([['', signature_table, '']], colWidths=[15, 520, 15])
    story.append(container_signature)

    def ajouter_pied_page(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#777777'))
        texte_page = f"Page {doc.page}"
        canvas.drawRightString(550, 20, texte_page)
        canvas.drawString(30, 20, "Devis généré automatiquement - Merci pour votre confiance.")
        canvas.restoreState()

    doc.build(story, onFirstPage=ajouter_pied_page, onLaterPages=ajouter_pied_page)
    buffer.seek(0)
    return buffer.getvalue()
