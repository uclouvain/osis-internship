from backoffice.settings import *

LOGGERS = {}

INSTALLED_APPS = tuple(INSTALLED_APPS) + (
    'django_extensions',
    'debug_toolbar',
)

MIDDLEWARE_CLASSES = tuple(MIDDLEWARE_CLASSES) + (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': "%s.true" % __name__,
}

def true(request):
    return True

import django
django.setup()