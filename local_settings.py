# -*- coding: utf-8 -*-
# Django local settings for ClipTube project.

import sys

PYTHON_EXEC = sys.executable

DEBUG = True
TEMPLATE_DEBUG = True

STATIC_ROOT = 'staticroot'

LOCAL_INSTALLED_APPS = [
    'debug_toolbar',
    'django_extensions',
]

LOCAL_MIDDLEWARE_CLASSES = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '../emails'

SERVE_STATIC = True

#TEMPLATE_STRING_IF_INVALID = '{{ %s }}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '../WorkLogs.db3',
    },
}


def apply_settings(settings):
    settings['INSTALLED_APPS'] = list(LOCAL_INSTALLED_APPS) + list(settings.get('INSTALLED_APPS'))

    settings['MIDDLEWARE_CLASSES'] = list(settings.get('MIDDLEWARE_CLASSES')) \
                                         + list(LOCAL_MIDDLEWARE_CLASSES)
