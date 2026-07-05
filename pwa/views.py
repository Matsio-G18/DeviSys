# pwa/views.py
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.shortcuts import render

def manifest(request):
    """Génère le fichier manifest.json unique de la PWA Don & Gloire"""
    data = {
        "name": "DeviSys Mobile",
        "short_name": "DeviSys",
        "description": "Générez et pilotez vos devis professionnels",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#252830",  # Gris foncé de votre logo
        "theme_color": "#00A3E0",       # Bleu Cyan de votre logo
        "orientation": "portrait-primary",
        "icons": [
            {
                "src": "/static/images/logo.jpeg", # Utilise votre logo
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return JsonResponse(data)

def service_worker(request):
    """Charge le fichier JavaScript du Service Worker"""
    template = loader.get_template('pwa/sw.js') # Déplacé dans le dossier pwa par propreté
    html = template.render({}, request)
    return HttpResponse(html, content_type='application/javascript')

def install(request):
    """Affiche la page d'installation personnalisée"""
    return render(request, 'pwa/install.html')
