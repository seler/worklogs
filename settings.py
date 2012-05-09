# -*- coding: utf-8 -*-
# Django settings for ClipTube project.

import os
import sys
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(PROJECT_PATH)

DEBUG = False
TEMPLATE_DEBUG = False

SESSION_COOKIE_AGE = 60 * 60 * 24 * 365
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
#SESSION_COOKIE_PATH = '/worklog_cookie/'

ADMINS = (
)

MANAGERS = (
)


INTERNAL_IPS = ('127.0.0.1',)

TEMPLATE_CONTEXT_PROCESSORS = (
        "django.contrib.auth.context_processors.auth",
        "django.core.context_processors.debug",
        "django.core.context_processors.i18n",
        "django.core.context_processors.media",
        "django.core.context_processors.static",
        "django.contrib.messages.context_processors.messages",
        'django.core.context_processors.request',
        )

API_IPS = (
    '127.0.0.1',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'WorkHours.db3',
    },
}

EMAIL_SUBJECT_PREFIX = 'WorkHours'
EMAIL_HOSTNAME = 'localhost'
EMAIL_HOST = 'localhost'

TIME_ZONE = 'Europe/Warsaw'

LANGUAGE_CODE = 'pl-pl'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

MEDIA_URL = '/media/'

# STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
STATIC_ROOT = ''

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_PATH, 'static'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = '=cv)(u_q=pl3f30e%0bp0dri67t5ec9=)argl0r9na7@17-dwf'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]


ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'templates'),
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',

    'worklogs',

    'south',
]

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

ugettext = lambda s: s


TINYMCE_DEFAULT_CONFIG = {
        'theme': 'advanced',
        'plugins': 'fullscreen,media,advlink,table,save,advimage,paste',
        'theme_advanced_buttons1': "save,|, bold,italic,underline,"
                                   "strikethrough,|,justifyleft,justifycenter,"
                                   "justifyright,justifyfull,|,styleselect,"
                                   "formatselect,fontselect,fontsizeselect,"
                                   "fullscreen,|,forecolor,backcolor",
        'theme_advanced_buttons2': "image, |, cut,copy,paste,pastetext,"
                                   "pasteword,|,search,replace,|,bullist,"
                                   "numlist,|,outdent,indent,blockquote,|,"
                                   "undo,redo,|,link,unlink,anchor,"
                                   "tablecontrols, code",
        'theme_advanced_toolbar_location': "top",
        'theme_advanced_toolbar_align': "left",
        'theme_advanced_toolbar_align': "left",
        'theme_advanced_statusbar_location': "bottom",
        'theme_advanced_resizing': 'true',
        'language': 'pl',
        'content_css': MEDIA_URL + "css/tiny_mce_content.css",
        'entity_encoding': 'raw',
        }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


try:
    from local_settings import *
except ImportError, e:
    # log.warning(repr(e))
    pass
else:
    if 'apply_settings' in globals():
        apply_settings(globals())
