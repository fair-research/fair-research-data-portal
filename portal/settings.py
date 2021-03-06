"""
Django settings for fair research project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from concierge import DEFAULT_CONCIERGE_SERVER

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SOCIAL_AUTH_GLOBUS_KEY = 'ebcaf30d-8148-4f1b-992a-bd089f823ac7'
# SOCIAL_AUTH_GLOBUS_SECRET = 'put this in portal/local_settings.py'
SECRET_KEY = 'use `openssl rand -hex 32` in local_settings.py in prod'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

WES_API = 'https://globusgenomics.fair-research.org/wes/'
JUPYTERHUB_STAGING = '5b552e84-7ae7-11e8-9443-0a6d4e044368'
CONCIERGE_SERVER = DEFAULT_CONCIERGE_SERVER
# Autostart the next task in a workspace if one exists
AUTO_START_NEXT_TASKS = True

PROJECT_TITLE = 'FAIR Research Data Portal'

# nihcommons-topmed
SEARCH_INDEX = 'd740440b-4f0f-4687-9573-0a7ce2ceda22'

LOGIN_URL = '/login/globus'
# Set to this on server
#SERVER_URL = '/4M.4.Fullstacks/'
SERVER_URL = ''

ENTRY_SERVICE_VARS = {
    'globus_group': 'globus_group',
    'globus_http_link': 'globus_http_link',
    'globus_http_scope': 'globus_http_scope',
    'remote_file_manifest': None,
    'Argon_GUID': 'minid',
}
DEFAULT_QUERY = '*'
# def generate_fake_manifests(var):
#     return [{
#         'url': var['http://gtex.globuscs.info/meta/GTEx_v7.xsd#Forward_path'],
#         'length': 2000000,
#         'md5': 'd16474427330f7c0a71dcbaf1d2a7a89',
#         'filename': os.path.basename(
#             var['http://gtex.globuscs.info/meta/GTEx_v7.xsd#Forward_path'])
#     }, {
#         'url': var['http://gtex.globuscs.info/meta/GTEx_v7.xsd#Reverse_path'],
#         'length': 2000000,
#         'md5': 'd16474427330f7c0a71dcbaf1d2a7a89',
#         'filename': os.path.basename(
#             var['http://gtex.globuscs.info/meta/GTEx_v7.xsd#Reverse_path'])
#         }]


SEARCH_ENTRY_FIELD_PATH = ''
SEARCH_SCHEMA = os.path.join(BASE_DIR, 'portal/search_schema.json')
SEARCH_MAPPER = ('portal.search', 'general_mapper')


SOCIAL_AUTH_GLOBUS_SCOPE = [
    'urn:globus:auth:scope:search.api.globus.org:search',
    'https://auth.globus.org/scopes/'
        '524361f2-e4a9-4bd0-a3a6-03e365cac8a9/concierge',
    'https://auth.globus.org/scopes/7ff68ee3-d931-4551-8f48-17964bda620e/gg',
    'https://auth.globus.org/scopes/identifiers.globus.org/view',
    'https://auth.globus.org/scopes/nih-commons.derivacloud.org/deriva_all',
    # 'https://auth.globus.org/scopes/56ceac29-e98a-440a-a594-b41e7a084b62/all'
]

ALLOWED_HOSTS = []

BAG_LIMIT = 100


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # This contains general Globus portal tools
    'globus_portal_framework',
    # This contains a search portal we will use for this demo
    'globus_portal_framework.search',
    'social_django',
    'portal',  # Added explicitly here only for Django admin autodiscovery
    'mp_auth',
    'api',
    'rest_framework',
    'django_filters',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
    # 'portal.middleware.ExpiredTokenMiddleware',
    'globus_portal_framework.middleware.ExpiredTokenMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'mp_auth.backends.mp.MultiproviderAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': ()
}

AUTHENTICATION_BACKENDS = [
    'globus_portal_framework.auth.GlobusOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

MULTIPROVIDER_AUTH = {
    "BearerTokens": {
        "globus": {
            "scope": [],
            "aud": "fair_research_data_portal"
        }
    },
    "JWT": {}
}

ROOT_URLCONF = 'portal.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'portal', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'globus_portal_framework.context_processors.globals',
                'portal.context_processors.globals',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'stream': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },

    'loggers': {
        'django.db.backends': {
                    'handlers': ['stream'],
                    # 'handlers': ['null'],  # Quiet by default!
                    # 'propagate': False,
                    'level': 'WARNING',
                    },
        'globus_portal_framework': {
            'handlers': ['stream'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'portal': {
            'handlers': ['stream'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'api': {
            'handlers': ['stream'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'mp_auth': {
            'handlers': ['stream'],
            'level': 'DEBUG',
            'propagate': True,
        }
    },
}

WSGI_APPLICATION = 'portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'aug_1st_nih_commons_demo.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.'
                'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Override any settings here if a local_settings.py file exists
try:
    from portal.local_settings import *
except ImportError:
    pass
