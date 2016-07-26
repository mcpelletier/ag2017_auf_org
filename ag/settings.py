# -*- encoding: utf-8 -*-
import os
import socket
import datetime
from django.utils.translation import gettext_lazy as _
from django.conf.global_settings import \
        TEMPLATE_CONTEXT_PROCESSORS as DEFAULT_TEMPLATE_CONTEXT_PROCESSORS

# Rapports d'erreurs
SERVER_EMAIL = 'ne-pas-repondre@auf.org'
EMAIL_SUBJECT_PREFIX = '[auf_ag - %s] ' % socket.gethostname()
ADMINS = ()
MANAGERS = ADMINS


TIME_ZONE = 'America/Montreal'

LANGUAGE_CODE = 'fr-ca'
gettext = lambda x: x
CMS_LANGUAGES = (
    ('fr', gettext('French')),
)

SITE_ID = 1
DEFAULT_LANGUAGE = 1

DATE_INPUT_FORMATS = ('%d/%m/%Y', '%Y-%m-%d')
DATE_FORMAT = 'j N Y'
SHORT_DATE_FORMAT = 'd/m/Y'
TIME_FORMAT = 'H:i'

PROJECT_ROOT = os.path.dirname(__file__)
SITE_ROOT = os.path.dirname(PROJECT_ROOT)

MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(SITE_ROOT, 'sitestatic')
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, 'static'),)

ROOT_URLCONF = 'ag.urls'

INSTALLED_APPS = (
    'filebrowser',
    'django.contrib.sites',
    'ag.core',
    'ag.inscription',
    'ag.gestion',
    'ag.outil',
    'ag.actualite',
    'ag.activites_scientifiques',
    'auf.django.auth',
    'auf.django.references',
    'auf.django.permissions',
    'auf.django.mailing',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'raven.contrib.django',
    'south',
    'crispy_forms',
    'sekizai',
    'cms',
    'cms.plugins.text',
    'menus',
    'mptt',
    'tinymce',
    'auf.django.pong',
    )

TEMPLATE_CONTEXT_PROCESSORS = DEFAULT_TEMPLATE_CONTEXT_PROCESSORS + (
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'cms.context_processors.media',
    'sekizai.context_processors.sekizai',
    'ag.outil.context_processors.list_Video',
    'ag.outil.context_processors.list_Video2',
    'ag.outil.context_processors.list_mot1',
    'ag.outil.context_processors.list_mot2',
    'ag.outil.context_processors.list_partenaire',
    'ag.outil.context_processors.list_slider',
    'ag.outil.context_processors.list_actu',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'ag.FrenchAdminMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'auf.django.piwik.middleware.TrackMiddleware',
    'auf.django.permissions.PermissionDeniedMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.transaction.TransactionMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',    
    'cms.middleware.user.CurrentUserMiddleware',    
    'cms.middleware.toolbar.ToolbarMiddleware',      
    'django.middleware.cache.FetchFromCacheMiddleware',
    )

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
)

gettext = lambda s: s

CMS_TEMPLATES = (
    ('accueil.html', gettext(u'Page Accueil')),
    ('page.html', gettext(u'Page Texte')),
    ('page_sous_rubrique.html', gettext(u'Page sous rubrique')),
    ('mot.html', gettext(u'Page Mot de recteur')),
    ('partenaire.html', gettext(u'Page Partenaire')),
    ('page_actu.html', gettext(u'Page Actualité')),
    ('video.html', gettext(u'Page Vidéo')),
    ('ateliers-scientifiques.html', gettext(u'Page Accueil ateliers')),
    ('atelier.html', gettext(u'Page atelier')),
)


SOUTH_TESTS_MIGRATE = False

ADMIN_TOOLS_INDEX_DASHBOARD = 'project.dashboard.CustomIndexDashboard'

MAILING_MODELE_PARAMS_ENVELOPPE = 'inscription.InvitationEnveloppe'
MAILING_TEMPORISATION = 2

AUTH_PROFILE_MODULE = 'core.UserProfile'
AUTHENTICATION_BACKENDS = (
    'auf.django.auth.backends.CascadeBackend',
    'django.contrib.auth.backends.ModelBackend',
    'auf.django.permissions.AuthenticationBackend',
    )
LOGIN_URL = '/connexion/'
LOGIN_REDIRECT_URL = '/gestion/'

CRISPY_TEMPLATE_PACK = 'uni_form'

SITE_ID = 1

PATH_FICHIERS_PARTICIPANTS = os.path.join(SITE_ROOT, 'medias_participants')
GESTION_AG_SENDER = 'ressources-informatiques@auf.org'

SENDFILE_BACKEND = 'sendfile.backends.simple'

ROLE_PROVIDERS = ('ag.gestion.role_provider', )

from conf import *  # NOQA

TINYMCE_DEFAULT_CONFIG = {
    'theme': "advanced",
    'theme_advanced_buttons1' : "formatselect,|,bold,italic,underline,|,bullist,numlist,|,undo,redo,|,link,unlink,image,|,backcolor,|removeformat,visualaid,code,",
    'theme_advanced_buttons2' : "",
    'theme_advanced_buttons3' : "",
    'theme_advanced_statusbar_location' : "bottom",
    'theme_advanced_toolbar_align' : "left",
    'width' : "800",
    'height' : "360",
    'theme_advanced_resizing' : "true",
    'custom_undo_redo_levels': 10,
    'theme_advanced_toolbar_location' : 'top',
}

DATE_FERMETURE_INSCRIPTIONS = datetime.date(2013, 3, 22)
