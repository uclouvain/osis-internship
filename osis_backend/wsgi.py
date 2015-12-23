"""
WSGI config for osis_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os,sys
try:
    from django.core.wsgi import get_wsgi_application
except(ImportError):
    sys.path.append("/home/osis/venvs/osis_backend_venv/lib/python3.4/site-packages")
    from django.core.wsgi import get_wsgi_application
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..' )
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../osis_backend')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osis_backend.settings")
application = get_wsgi_application()

