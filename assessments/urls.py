##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from assessments.views import score_encoding, scores_responsible, upload_xls_utils

urlpatterns = [
    url(r'^scores_responsible/$', scores_responsible.scores_responsible, name='scores_responsible'),
    url(r'^scores_responsible_search$', scores_responsible.scores_responsible_search, name='scores_responsible_search'),
    url(r'^scores_responsible_management/(?P<pk>[0-9]+)/edit/$', scores_responsible.scores_responsible_management,
        name='scores_responsible_management'),
    url(r'^scores_responsible_delete/(?P<pk>[0-9]+)/edit/$', scores_responsible.scores_responsible_delete,
        name='scores_responsible_delete'),
    url(r'^scores_responsible_add', scores_responsible.scores_responsible_add, name='scores_responsible_add'),
    url(r'^scores_responsible_management$', scores_responsible.scores_responsible_list),
    url(r'^scores_encoding/outside_period/$',
        score_encoding.outside_period, name='outside_scores_encodings_period'),
    url(r'^scores_encoding/$', score_encoding.scores_encoding, name='scores_encoding'),
    url(r'^scores_encoding/online/(?P<learning_unit_year_id>[0-9]+)/$',
        score_encoding.online_encoding, name='online_encoding'),
    url(r'^scores_encoding/online/(?P<learning_unit_year_id>[0-9]+)/form$',
        score_encoding.online_encoding_form, name='online_encoding_form'),
    url(r'^scores_encoding/online/([0-9]+)/submission$',
        score_encoding.online_encoding_submission, name='online_encoding_submission'),
    url(r'^scores_encoding/online/(?P<learning_unit_year_id>[0-9]+)/double_form$',
        score_encoding.online_double_encoding_form, name='online_double_encoding_form'),
    url(r'^scores_encoding/online/(?P<learning_unit_year_id>[0-9]+)(?:/(?P<tutor_id>[0-9]+))?/double_validation$',
        score_encoding.online_double_encoding_validation, name='online_double_encoding_validation'),
    url(r'^scores_encoding/specific_criteria/$',
        score_encoding.specific_criteria, name='specific_criteria'),
    url(r'^scores_encoding/specific_criteria/submission/$',
        score_encoding.specific_criteria_submission, name='specific_criteria_submission'),
    url(r'^scores_encoding/specific_criteria/search/$',
        score_encoding.search_by_specific_criteria, name='search_by_specific_criteria'),
    url(r'^scores_encoding/notes_printing_all(?:/(?P<tutor_id>[0-9]+))?(?:/(?P<offer_id>[0-9]+))?/$',
        score_encoding.notes_printing_all, name='notes_printing_all'),
    url(r'^scores_encoding/notes_printing/(?P<learning_unit_year_id>[0-9]+)(?:/(?P<tutor_id>[0-9]+))?/$',
        score_encoding.notes_printing, name='notes_printing'),
    url(r'^scores_encoding/xlsdownload/([0-9]+)/$',
        score_encoding.export_xls, name='scores_encoding_download'),
    url(r'^scores_encoding/upload/(?P<learning_unit_year_id>[0-9]+)/$',
        upload_xls_utils.upload_scores_file, name='upload_encoding'),
    url(r'', score_encoding.assessments, name="assessments")
]
