from .settings_base import *
try:
    from .local import *
except ImportError:
    pass

#DEBUG = True
#ALLOWED_HOSTS = ['*']
#INSTALLED_APPS += ['marcus.apps.MarcusConfig']
