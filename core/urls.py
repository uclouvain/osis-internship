from django.conf.urls import url
from django.contrib.auth.views import login,logout

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),

    # login / logout urls
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^studies/$', views.studies, name='studies'),
    url(r'^studies/assessements/$', views.assessements, name='assessements'),
    url(r'^studies/assessements/scores_encoding$', views.scores_encoding, name='scores_encoding'),
    url(r'^studies/assessements/scores_encoding/online/([0-9]+)/$', views.online_encoding, name='online_encoding')
]
