from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^studies/assessements/$', views.assessements)]
