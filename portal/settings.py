"""
Django settings for fair research project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

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

PROJECT_TITLE = 'FAIR Research Data Portal'

# Perf data index for example only. Change to your index when you're ready
SEARCH_INDEX = '766b9766-3943-429f-a509-0433c9cbd5da'


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

ENTRY_SERVICE_VARS = {
    'remote_file_manifest': None,
}

SEARCH_ENTRY_FIELD_PATH = ''
SEARCH_SCHEMA = os.path.join(BASE_DIR, 'portal/search_schema.json')
SEARCH_MAPPER = ('portal.search', 'general_mapper')


SOCIAL_AUTH_GLOBUS_SCOPE = [
    'urn:globus:auth:scope:search.api.globus.org:search',
    'urn:globus:auth:scope:transfer.api.globus.org:all',
    # 'https://auth.globus.org/scopes/56ceac29-e98a-440a-a594-b41e7a084b62/all'
]

ALLOWED_HOSTS = []

BAG_LIMIT = 50


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
    'globus_portal_framework.middleware.ExpiredTokenMiddleware',

]

AUTHENTICATION_BACKENDS = [
    'globus_portal_framework.auth.GlobusOAuth2',
    'django.contrib.auth.backends.ModelBackend',
]

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
        }
    },
}

WSGI_APPLICATION = 'portal.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
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
