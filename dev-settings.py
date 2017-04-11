from backoffice.settings.local import *
LOGGERS = {}

del QUEUES

if DEBUG:
    INSTALLED_APPS = INSTALLED_APPS + (
        'django_extensions',
        'debug_toolbar',
    )

    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )

    INTERNAL_IPS = ('127.0.0.1',)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
    }