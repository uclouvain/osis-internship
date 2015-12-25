from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('core.urls')),
]

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.access_denied'