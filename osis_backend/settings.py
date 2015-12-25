import os

from django.core.urlresolvers import reverse_lazy

import logging
import configparser


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

logger = logging.getLogger(__name__)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'chgajy@#q91^!6owmz29%@#3jw094@yr@1!6w3lxx@n6v!7nvd'

# Analyse in which environment the application is running
config = configparser.ConfigParser()
server_env = None

# Database default config
DB_ENGINE = 'django.db.backends.sqlite3'
DB_NAME = 'osis_backend_local'
DB_USER = ''
DB_PASSWORD = ''
DB_HOST = ''
DB_PORT = ''

try:
    config.read('/home/osis/ConfigFile.properties')
    server_env = config.get('ServerProperties', 'server.env')
    SECRET_KEY = config.get('DjangoProperties', 'secret_key')
    DB_ENGINE = config.get('DbProperties', 'db.engine')
    DB_NAME = config.get('DbProperties', 'db.name')
    DB_USER = config.get('DbProperties', 'db.user')
    DB_PASSWORD = config.get('DbProperties', 'db.password')
    DB_HOST = config.get('DbProperties', 'db.host')
    DB_PORT = config.get('DbProperties', 'db.port')

    logger.info('SERVER : ' + server_env)
except Exception as e:
    logger.info('SERVER : Local')
    pass


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/


ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core'
)

if server_env is not None and server_env != 'LOCAL':
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'core.authentication.shibbollethUser.ShibbollethUserMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
    )
    AUTHENTICATION_BACKENDS = [
        'core.authentication.shibbollethUser.ShibbollethUserBackend',
    ]

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': 'home/osis/django_logs/debug.log',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
else:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'django.middleware.security.SecurityMiddleware',
    )

if server_env is None or server_env == 'DEV' or server_env == 'LOCAL':
    DEBUG = True
else:
    DEBUG = False

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': DB_ENGINE,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    }
}

ROOT_URLCONF = 'osis_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'osis_backend.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'fr-be'

TIME_ZONE = 'Europe/Brussels'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

LOGIN_URL = reverse_lazy('login')
LOGOUT_URL = reverse_lazy('logout')
LOGIN_REDIRECT_URL = '/'

FIXTURE_DIRS = (
    '/core/fixtures/',
)
