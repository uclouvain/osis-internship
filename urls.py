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
from django.conf.urls import include, url

from internship.views import (affectation, home, internship, master, offer, period, place, speciality,
                              student_resume, cohort, upload_xls)

urlpatterns = [
    url(r'^$', home.view_cohort_selection, name='internship'),
    url(r'^student/get$', student_resume.get_student, name='internship_student_get'),

    url(r'^cohorts/', include([
        url(r'^new$', cohort.new, name='cohort_new'),
        url(r'^edit/(?P<cohort_id>[0-9]+)$', cohort.edit, name='cohort_edit'),

        url(r'^(?P<cohort_id>[0-9]+)/', include([
            url(r'^$', home.cohort_home, name='internships_home'),

            url(r'^internships/', include([
                url(r'^$', internship.internship_list, name='internship-list'),
                url(r'^new$', internship.internship_new, name='internship-new'),
                url(r'^edit/(?P<internship_id>[0-9]+)$', internship.internship_edit, name='internship-edit'),
                url(r'^delete/(?P<internship_id>[0-9]+)$', internship.internship_delete, name='internship-delete')
            ])),

            url(r'^masters/', include([
                url(r'^$', master.masters, name='internships_masters'),
                url(r'^(?P<master_id>[0-9]+)$', master.master, name='master'),
                url(r'^(?P<master_id>[0-9]+)/form/$', master.master_form, name='master_edit'),
                url(r'^form/$', master.master_form, name='master_new'),
                url(r'^save/$', master.master_save, name="master_save"),
                url(r'^import/$', master.master_import, name="master_import")
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
                url(r'^(?P<organization_id>[0-9]+)/edit/$', place.organization_edit, name='place_edit'),
                url(r'^exportxls/(?P<organization_id>[0-9]+)/master/$', place.export_organisation_affectation_master,
                    name='export_organisation_affectation_master'),
                url(r'^exportxls/(?P<organization_id>[0-9]+)/hospital/$', place.export_organisation_affectation_hospital,
                    name='export_organisation_affectation_hospital'),
                url(r'^save/(?P<organization_id>[0-9]+)/$', place.place_save,
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
                url(r'^$', student_resume.internships_student_resume, name='internships_student_resume'),
                url(r'^form/$', student_resume.student_form, name='internship_student_form'),
                url(r'^save/$', student_resume.student_save, name="internship_student_save"),
                url(r'^(?P<student_id>[0-9]+)/', include([
                    url(r'^resume/$', student_resume.internships_student_read, name='internships_student_read'),

                    url(r'^information/modification/$', student_resume.internship_student_information_modification,
                        name='internship_student_information_modification'),
                    url(r'^information/modification/save/$', student_resume.student_save_information_modification,
                        name='student_save_information_modification'),

                    url(r'^affectation/modification/$', student_resume.internship_student_affectation_modification,
                        name='internship_student_affectation_modification'),
                    url(r'^affectation/modification/save/$', student_resume.student_save_affectation_modification,
                        name='student_save_affectation_modification'),

                    url(r'^modification/$', internship.internships_modification_student,
                        name='internships_modification_student'),

                    url(r'^(?P<internship_id>[0-9]+)/', include([
                        url(r'^modification/$', internship.internships_modification_student,
                            name='switch_internship'),
                        url(r'^switch_speciality/$',
                            internship.assign_speciality_for_internship, name='switch_speciality'),
                        url(r'^(?P<speciality_id>[0-9]+)/modification/$',
                            internship.internships_modification_student, name='specific_internship_student_modification'),
                    ])),
                ])),
            ])),

            url(r'^affectation_result/', include([
                url(r'^$', affectation.view_hospitals, name='internship_affectation_hospitals'),
                url(r'^students/$', affectation.view_students, name='internship_affectation_students'),
                url(r'^statistics/$', affectation.view_statistics, name='internship_affectation_statistics'),
                url(r'^errors/$', affectation.view_errors, name='internship_affectation_errors'),

                url(r'^score_encoding/xls$', affectation.export_score_encoding_xls, name="export_score_encoding_xls"),
                url(r'^generate/$', affectation.run_affectation, name='internship_affectation_generate'),
                url(r'^sumup/$', affectation.internship_affectation_sumup, name='internship_affectation_sumup'),
            ])),

            url(r'^internships/upload/$', upload_xls.upload_internships_file, name='upload_internship'),
        ])),

    ])),
]
