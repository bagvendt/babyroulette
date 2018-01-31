from .settings_base import *
try:
    from .anneogvidir_local import *
except ImportError:
    pass

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS += ['anneogvidir.apps.AnneogvidirConfig']
STARTING_CREDITS = 1000

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'anneogvidir.sqlite3'),
    }
}