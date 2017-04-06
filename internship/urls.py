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
from django.conf.urls import include, url

from internship.utils import upload_xls
from internship.views import (affectation_statistics, home, internship, master,
                              offer, period, place, speciality, student_resume,
                              cohort)

urlpatterns = [
    url(r'^$', home.view_cohort_selection, name='internship'),

    url(r'^cohorts/', include([
        url(r'^new$', cohort.new, name='cohort_new'),

        url(r'^edit/(?P<cohort_id>[0-9]+)$', cohort.edit, name='cohort_edit'),
        url(r'^(?P<cohort_id>[0-9]+)/', include([
            url(r'^$', home.cohort_home, name='internships_home'),

            url(r'^masters/', include([
                url(r'^$', master.internships_masters, name='internships_masters'),
                url(r'^delete/$', master.delete_internships_masters, name='delete_internships_masters'),
                url(r'^upload/$', upload_xls.upload_masters_file, name='upload_internships_masters'),
            ])),

            url(r'^offers/', include([
                url(r'^$', offer.internships, name='internships'),
                url(r'^(?P<offer_id>[0-9]+)/students/choice/$', offer.student_choice,
                    name='internship_detail_student_choice'),
                url(r'^block/$', offer.internships_block, name='internships_block'),
                url(r'^save/$', offer.internships_save, name='internships_save'),
                url(r'^save/modification/student/$', offer.internship_save_modification_student,
                    name='internship_save_modification_student'),
            ])),

            url(r'^periods/', include([
                url(r'^$', period.internships_periods, name='internships_periods'),
                url(r'^create/$', period.period_create, name='periods_create'),
                url(r'^delete/(?P<period_id>[0-9]+)/$', period.period_delete, name='period_delete'),
                url(r'^(?P<period_id>[0-9]+)/$', period.period_get, name='period_get'),
                url(r'^new/$', period.period_new, name='period_new'),
                url(r'^save/(?P<period_id>[0-9]+)/$', period.period_save, name='period_save')
            ])),

            url(r'^period_places/', include([
                url(r'^edit/(?P<internship_id>[0-9]+)/$', internship.edit_period_places, name='edit_period_places'),
                url(r'^save/(?P<internship_id>[0-9]+)/$', internship.save_period_places, name='save_period_places'),
            ])),

            url(r'^places/', include([
                url(r'^$', place.internships_places, name='internships_places'),
                url(r'^(?P<organization_id>[0-9]+)/students/affectation/$', place.student_affectation,
                    name='place_detail_student_affectation'),
                url(r'^(?P<organization_id>[0-9]+)/students/choice/$', place.student_choice,
                    name='place_detail_student_choice'),
                url(r'^create/$', place.organization_create, name='place_create'),
                url(r'^edit/(?P<organization_id>[0-9]+)/$', place.organization_edit, name='place_edit'),
                # url(r'^exportpdf/([0-9]+)/([0-9]+)/$', place.export_pdf, name='affectation_download_pdf'),
                url(r'^exportxls/(?P<organization_id>[0-9]+)/(?P<speciality_id>[0-9]+)/$', place.export_xls,
                    name='affectation_download'),
                url(r'^exportxls/(?P<organization_id>[0-9]+)/$', place.export_organisation_affectation_as_xls,
                    name='organisation_affectation_download'),
                url(r'^save/(?P<organization_id>[0-9]+)/(?P<organization_address_id>[0-9]+)/$', place.place_save,
                    name='place_save'),
                url(r'^save/$', place.organization_new, name='place_save_new'),
                url(r'^upload/$', upload_xls.upload_places_file, name='upload_places'),
            ])),

            url(r'^specialities/', include([
                url(r'^$', speciality.specialities, name='internships_specialities'),
                url(r'^create/$', speciality.speciality_create, name='speciality_create'),
                url(r'^delete/(?P<speciality_id>[0-9]+)/$', speciality.speciality_delete, name='speciality_delete'),
                url(r'^modification/(?P<speciality_id>[0-9]+)/$', speciality.speciality_modification,
                    name='speciality_modification'),
                url(r'^new/$', speciality.speciality_new, name='speciality_new'),
                url(r'^save/(?P<speciality_id>[0-9]+)/$', speciality.speciality_save, name='speciality_save'),
            ])),

            url(r'^students/', include([
                url(r'^resume/$', student_resume.internships_student_resume, name='internships_student_resume'),
            ])),

            url(r'^affectation_result/', include([
                url(r'^$', affectation_statistics.internship_affectation_statistics,
                    name='internship_affectation_statistics'),
                url(r'^sumup/$', affectation_statistics.internship_affectation_sumup,
                    name='internship_affectation_sumup'),
            ])),

            url(r'^students/', include([
                url(r'^(?P<student_id>[0-9]+)/', include([
                    url(r'^affectation/modification/$', student_resume.internship_student_affectation_modification,
                        name='internship_student_affectation_modification'),
                    url(r'^information/modification/$', student_resume.internship_student_information_modification,
                        name='internship_student_information_modification'),
                    url(r'^resume/$', student_resume.internships_student_read, name='internships_student_read'),
                    url(r'^save/information/modification/$', student_resume.student_save_information_modification,
                        name='student_save_information_modification'),
                    url(r'^save/affectation/modification/$', student_resume.student_save_affectation_modification,
                        name='student_save_affectation_modification'),
                ])),
            ])),

            url(r'^student/(?P<student_id>[0-9]+)/', include([
                url(r'^modification/$', internship.internships_modification_student,
                    name='internships_modification_student'),
                url(r'^(?P<internship_id>[0-9]+)/modification/$', internship.internships_modification_student,
                    name='switch_internship'),
                url(r'^(?P<internship_id>[0-9]+)/(?P<speciality_id>[0-9]+)/modification/$',
                    internship.internships_modification_student, name='specific_internship_student_modification'),
            ])),

            url(r'^switch_speciality/(?P<student_id>[0-9]+)/(?P<internship_id>[0-9]+)/$',
                internship.assign_speciality_for_internship, name='switch_speciality'),
            url(r'^internships/upload/$', upload_xls.upload_internships_file, name='upload_internship'),
        ])),

    ])),


        # url(r'^resume/$', student_resume.internships_student_resume, name='internships_student_resume'),
]
