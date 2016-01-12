from django.conf.urls import url
from django.contrib.auth.views import login,logout

from . import views

from . import exportUtils
from . import uploadXlsUtils

urlpatterns = [
    url(r'^$', views.home, name='home'),

    # login / logout urls
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^studies/$', views.studies, name='studies'),
    url(r'^studies/assessements/$', views.assessements, name='assessements'),
    url(r'^studies/assessements/scores_encoding$', views.scores_encoding, name='scores_encoding'),
    url(r'^studies/assessements/all_notes_printing/([0-9]+)/$', views.all_notes_printing, name='all_notes_printing'),
    url(r'^studies/assessements/notes_printing/([0-9]+)/([0-9]+)/$', views.notes_printing, name='notes_printing'),
    url(r'^studies/assessements/scores_encoding/online/([0-9]+)/$', views.online_encoding, name='online_encoding'),
    url(r'^studies/assessements/scores_encoding/xlsdownload/([0-9]+)/([0-9]+)/([0-9]+)/$',exportUtils.export_xls, name='scores_encoding_download'),
    url(r'^studies/assessements/scores_encoding/download/([0-9]+)/$',views.download_scores_file,name='donwload_scores_file'),
    url(r'^studies/assessements/scores_encoding/upload/([0-9]+)/([0-9]+)/([0-9]+)/$',uploadXlsUtils.upload_scores_file,name='upload_encoding'),
    url(r'^studies/assessements/scores_encoding/upload_score_error$',views.upload_score_error,name='upload_score_error'),

]
