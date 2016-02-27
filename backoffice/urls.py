##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import string
from django.conf.urls import include, url
from django.contrib import admin
import random
import re
from backoffice.settings import PROPERTIES_FILE

ADMIN_PAGE_URL = 'admin'
if PROPERTIES_FILE :
    import configparser
    config = configparser.ConfigParser()
    config.read(PROPERTIES_FILE)
    if config['ADMINISTRATION']['admin_page']:
        ADMIN_PAGE_URL = config['ADMINISTRATION']['admin_page']



urlpatterns = [
    url(r'^'+re.escape(ADMIN_PAGE_URL)+r'/', admin.site.urls),
    url(r'', include('base.urls')),
    url(r'', include('internship.urls')),
]

handler404 = 'base.views.common.page_not_found'
handler403 = 'base.views.common.access_denied'

admin.site.site_header = 'OSIS'
admin.site.site_title  = 'OSIS'
admin.site.index_title = 'Louvain'
