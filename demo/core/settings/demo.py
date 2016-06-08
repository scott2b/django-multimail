# Django settings for multimail demo project.
import os, sys
from os import environ as env

PROJECT_NAME = 'django-multimail'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get('SECRET_KEY', 'development-mode-not-secret')

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOWED_HOSTS = env.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split()

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'multimail'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': env.get(
            'DEFAULT_DB_ENGINE',
            'django.db.backends.postgresql_psycopg2' # postgres
            # 'django.db.backends.sqlite3' # sqlite3
        ),
        'NAME': env.get(
            'DEFAULT_DB_NAME',
            PROJECT_NAME # postgres
            # join(BASE_DIR, 'db.sqlite3') # sqlite3
        ),
        'USER': env.get('DEFAULT_DB_USER', PROJECT_NAME),
        'PASSWORD': env.get('DEFAULT_DB_PASSWORD', PROJECT_NAME),
        'HOST': env.get('DEFAULT_DB_HOST', '127.0.0.1'),
        'PORT': env.get(
            'DEFAULT_DB_PORT',
            '5432' # postgres
            # '' # sqlite3
        )
    }
}

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'multimail_static')
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
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

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
MULTIMAIL_DELETE_PRIMARY = True
MULTIMAIL_POST_VERIFY_URL = '/profile/'
