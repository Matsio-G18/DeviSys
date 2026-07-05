import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ==============================================================================
# CONFIGURATION DE SÉCURITÉ ET DÉVELOPPEMENT (SÉCURISÉE POUR RENDER)
# ==============================================================================

# Récupère la clé secrète depuis l'environnement sur Render, ou utilise la clé locale en développement
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-_8g9#=a83&pntpwnprx)=c%3b3z*a0s-nh5mf7qw)wl)cb2e1x')

# Passe automatiquement à False en production si la variable DEBUG n'est pas définie sur True
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Autoriser localhost pour le développement et toutes les URLs générées par Render en production
if not DEBUG:
    ALLOWED_HOSTS = ['devisys.onrender.com', '127.0.0.1', 'localhost', '[::1]']
else:
    ALLOWED_HOSTS = ['*']


# ==============================================================================
# APPLICATIONS ET MIDDLEWARES
# ==============================================================================

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Vos applications locales
    'core',
    'clients',
    'devis',
    'pdfgen',
    'pwa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Gestion optimisée des fichiers statiques
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Protection CSRF active
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app_devis.urls'


# ==============================================================================
# TEMPLATES ET INTERFACES GRAPHIQUES
# ==============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Activation du dossier global de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'app_devis.wsgi.application'


# ==============================================================================
# BASE DE DONNÉES (SQLite3 pour le développement)
# ==============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==============================================================================
# VALIDATION DES MOTS DE PASSE
# ==============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ==============================================================================
# INTERNATIONALISATION (Passage en Français & Fuseau Horaire Congo)
# ==============================================================================

LANGUAGE_CODE = 'fr-fr' # Formulaires et messages d'erreur système en Français

TIME_ZONE = 'Africa/Brazzaville' # Heure locale pour l'émission des devis

USE_I18N = True

USE_TZ = True


# ==============================================================================
# GESTION DES FICHIERS STATIQUES (CSS, JS, AdminLTE)
# ==============================================================================

STATIC_URL = 'static/'

# Emplacements des assets en développement
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Dossier de destination pour la production (requis par collectstatic)
STATIC_ROOT = BASE_DIR / 'staticfiles'

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ==============================================================================
# CONFIGURATION DES REDIRECTIONS D'AUTHENTIFICATION (AUTHENTICATION)
# ==============================================================================

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/'  # Redirige explicitement vers la racine après succès
LOGOUT_REDIRECT_URL = 'login'


# ==============================================================================
# CORRECTIF ERREUR CSRF / POLITIQUES DE COOKIES (Sécurité locale)
# ==============================================================================

# Assure la compatibilité des jetons d'identification sur le port de développement 8000
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = False  # Permet à l'interface de lire le jeton lors des requêtes POST

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==============================================================================
# CONFIGURATION DES ENVOIS D'EMAILS
# ==============================================================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '://gmail.com'                # Serveur SMTP de votre fournisseur
EMAIL_PORT = 587                             # Port standard sécurisé
EMAIL_USE_TLS = True                         # Chiffrement requis
EMAIL_HOST_USER = 'donimatsiona@gmail.com'  # Votre adresse e-mail professionnelle

# Sécurisation du mot de passe de l'application SMTP
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'dxpb ocjz eqzh aazf')
DEFAULT_FROM_EMAIL = f"Don & Gloire - DeviSys Solutions <{EMAIL_HOST_USER}>"


# ==============================================================================
# INTERFACE DE GESTION JAZZMIN
# ==============================================================================

JAZZMIN_SETTINGS = {
    # Titre de la fenêtre du navigateur
    "site_title": "Don & Gloire - Devis",
    
    # Titre sur l'écran de connexion
    "site_header": "Application Devis",
    
    # Texte de marque en haut à gauche
    "site_brand": "Devis Manager",
    
    # Message de bienvenue sur l'écran de connexion
    "welcome_sign": "Bienvenue dans votre gestionnaire de devis",
    
    # Droits d'auteur dans le pied de page
    "copyright": "App Devis Ltd Don & Gloire",
    
    # Recherche globale sur le site pour vos clients ou devis
    "search_model": ["clients.Client", "devis.Devis"],
    
    "custom_css": "core/css/admin_custom.css",
    
    # 1. METTRE EN VALEUR LES MENUS PRINCIPAUX
    "topmenu_links": [
        {"name": "Accueil", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"model": "devis.Devis"},
        {"model": "clients.Client"},
    ],
    
    # 2. ACTIVER LE PERSONNALISEUR DE THÈME EN DIRECT
    "show_ui_builder": True,
    
    # Forme des icônes pour le menu latéral
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "clients.Client": "fas fa-address-card",
        "devis.Devis": "fas fa-file-invoice-dollar",
        "devis.SectionDevis": "fas fa-folder",
    },
}

JAZZMIN_UI_TWEAKS = {
    # Thème général clair et professionnel
    "theme": "corporate",
    
    # Barre du haut en Bleu Foncé (Style Navy)
    "navbar": "navbar-dark bg-primary",
    
    # Liens ou éléments actifs colorés avec votre Orange Foncé
    "brand_colour": "navbar-orange",
    
    # Menu latéral gauche en style sombre pour faire ressortir le texte
    "sidebar": "sidebar-dark-primary",
    
    # Accentuation des boutons et liens sur l'Orange Foncé
    "accent": "accent-orange",
    
    # Petits ajustements de design modernes
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
}
