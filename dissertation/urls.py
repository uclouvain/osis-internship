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
from django.conf.urls import url
from dissertation.views import dissertation,proposition_dissertation,information

urlpatterns = [
    url(r'^$', dissertation.dissertations, name='dissertations'),

    url(r'^informations/$', information.informations, name='informations'),
    url(r'^informations_edit/$', information.informations_edit, name='informations_edit'),

    url(r'^proposition_dissertations/$', proposition_dissertation.proposition_dissertations, name='proposition_dissertations'),
    url(r'^proposition_dissertation/(?P<pk>[0-9]+)/edit/$', proposition_dissertation.proposition_dissertation_edit, name='proposition_dissertation_edit'),
    url(r'^proposition_dissertation_detail/(?P<pk>[0-9]+)/$', proposition_dissertation.proposition_dissertation_detail, name='proposition_dissertation_detail'),
    url(r'^proposition_dissertation_new$', proposition_dissertation.proposition_dissertation_new, name='proposition_dissertation_new'),
    url(r'^proposition_dissertation_my$', proposition_dissertation.proposition_dissertation_my, name='proposition_dissertation_my'),

    url(r'^search$', proposition_dissertation.proposition_dissertations_search, name='proposition_dissertations_search'),
]
