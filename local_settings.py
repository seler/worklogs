# -*- coding: utf-8 -*-
# Django local settings for ClipTube project.

import sys

PYTHON_EXEC = sys.executable

DEBUG = True
TEMPLATE_DEBUG = True

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "guest"
BROKER_PASSWORD = "guest"
BROKER_VHOST = "/"

CELERYD_CONCURRENCY = 1

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

SAFE_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MOGILEFS_MEDIA_URL = '/media/'
DYNAMIC_MEDIA_URL = '/media/'
SAFE_MEDIA_URL = '/media/'

SITE_HOST = 'localhost'
SITE_DOMAIN = 'localhost'

VIDEO_TMP = '/tmp/video'

TEST_VIDEO = '/home/rselewonko/dev/BigBuckBunnyTrailer.mov'
TEST_VIDEO_WIDTH = 854
TEST_VIDEO_HEIGHT = 480
TEST_VIDEO_DURATION = 33
TEST_VIDEO_ASPECT_RATIO = 16. / 9.

DEFAULT_CHANNEL_SLUG = 'glowny'

#TEMPLATE_STRING_IF_INVALID = '{{ %s }}'

ZASLEPKA = 'lena.png'
RATINGS_VOTES_PER_IP = 9999999
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
