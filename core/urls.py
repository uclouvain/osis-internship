from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^studies/assessements/$', views.assessements)]
