from .settings_base import *
try:
    from .marcus_local import *
except ImportError:
    pass

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS += ['marcus.apps.MarcusConfig']
STARTING_CREDITS = 1000

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'marcus.sqlite3'),
    }
}