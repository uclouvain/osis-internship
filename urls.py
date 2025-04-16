##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.urls import include
from django.urls import path, re_path

from internship.views import (
    affectation, home, internship, master, offer, period, place, score, speciality, student, cohort, place_evaluation,
)

urlpatterns = [
    path('', home.view_cohort_selection, name='internship'),
    path('student/get', student.get_student, name='internship_student_get'),

    path('cohorts/', include([
        path('new', cohort.new, name='cohort_new'),
        path('edit/<int:cohort_id>', cohort.edit, name='cohort_edit'),

        path('<int:cohort_id>/', include([
            path('', home.cohort_home, name='internships_home'),

            path('internships/', include([
                path('', internship.internship_list, name='internship-list'),
                path('new', internship.internship_new, name='internship-new'),
                path('edit/<int:internship_id>', internship.internship_edit, name='internship-edit'),
                path('delete/<int:internship_id>', internship.internship_delete, name='internship-delete')
            ])),

            path('masters/', include([
                path('', master.masters, name='internships_masters'),
                path('<int:master_id>', master.master, name='master'),
                path('<int:master_id>/form/', master.master_form, name='master_edit'),
                path('create_accounts/', master.create_user_accounts, name='create_accounts'),
                path('transfer_allocation/', master.transfer_master_allocation_to_cohort, name='transfer_allocation'),
                path('extend_validity/', master.extend_accounts_validity, name='extend_validity'),
                path('form/', master.master_form, name='master_new'),
                path('form/ajax/person_exists/', master.person_exists, name='person_exists'),
                path('save/', master.master_save, name="master_save"),
                path('delete/<int:master_id>', master.master_delete, name="master_delete"),
                path('export/', master.export_masters, name='master_export'),
            ])),

            path('offers/', include([
                path('', offer.list_internships, name='internships'),
                path('<int:specialty_id>', offer.list_internships, name='internships'),
                path('<int:offer_id>/students/choice/', offer.student_choice,
                     name='internship_detail_student_choice'),
                path('save/', offer.internships_save, name='internships_save'),
                path('save/modification/student/', offer.internship_save_modification_student,
                     name='internship_save_modification_student'),
                path('upload/', offer.upload_offers, name='upload_offers'),
            ])),

            path('periods/', include([
                path('', period.internships_periods, name='internships_periods'),
                path('create/', period.period_create, name='periods_create'),
                path('delete/<int:period_id>/', period.period_delete, name='period_delete'),
                path('<int:period_id>/', period.period_get, name='period_get'),
                path('new/', period.period_new, name='period_new'),
                path('save/<int:period_id>/', period.period_save, name='period_save')
            ])),

            path('period_places/', include([
                path('edit/<int:internship_id>/', internship.edit_period_places, name='edit_period_places'),
                path('save/<int:internship_id>/', internship.save_period_places, name='save_period_places'),
            ])),

            path('places/', include([
                path('', place.internships_places, name='internships_places'),
                path('create/', place.organization_create, name='place_create'),
                path('save/', place.organization_new, name='place_save_new'),

                path('<int:organization_id>/', include([
                    path('students/affectation/', place.student_affectation, name='place_detail_student_affectation'),
                    path('students/choice/', place.student_choice, name='place_detail_student_choice'),
                    path('edit/', place.organization_edit, name='place_edit'),
                    path('save/', place.place_save, name='place_save'),
                    path('remove/', place.place_remove, name='place_remove'),
                    path('exportxls/master/', place.export_organisation_affectation_master,
                         name='export_organisation_affectation_master'),
                    path('exportxls/hospital/', place.export_hospital_affectation,
                         name='export_organisation_affectation_hospital'),
                ]))
            ])),

            path('specialities/', include([
                path('', speciality.specialities, name='internships_specialities'),
                path('create/', speciality.speciality_create, name='speciality_create'),
                path('new/', speciality.speciality_new, name='speciality_new'),
                path('<int:speciality_id>/', include([
                    path('delete/', speciality.speciality_delete, name='speciality_delete'),
                    path('modification/', speciality.modify, name='speciality_modification'),
                    path('save/', speciality.speciality_save, name='speciality_save'),
                ])),
            ])),

            path('students/', include([
                path('', student.internships_student_resume, name='internships_student_resume'),
                path('form/', student.student_form, name='internship_student_form'),
                path('save/', student.student_save, name="internship_student_save"),
                path('import/', include([
                    path('', student.import_students, name="internship_students_import"),
                    path('update/', student.internships_student_import_update,
                         name='internships_student_import_update'),
                ])),
                path('<int:student_id>/', include([
                    path('resume/', student.internships_student_read, name='internships_student_read'),
                    path('information/modification/', student.internship_student_information_modification,
                         name='internship_student_information_modification'),
                    path('information/modification/save/', student.student_save_information_modification,
                         name='student_save_information_modification'),
                    path('affectation/modification/', student.internship_student_affectation_modification,
                         name='internship_student_affectation_modification'),
                    path('affectation/modification/save/', student.student_save_affectation_modification,
                         name='student_save_affectation_modification'),
                    path('modification/', internship.modification_student, name='internships_modification_student'),
                    path('<int:internship_id>/', include([
                        path('modification/', internship.modification_student, name='switch_internship'),
                        path('switch_speciality/', internship.assign_speciality_for_internship,
                             name='switch_speciality'),
                        path('<int:speciality_id>/modification/', internship.modification_student,
                             name='specific_internship_student_modification'),
                    ])),
                ])),
            ])),

            path('affectation_result/', include([
                path('', affectation.view_hospitals, name='internship_affectation_hospitals'),
                path('students/', affectation.view_students, name='internship_affectation_students'),
                path('statistics/', affectation.view_statistics, name='internship_affectation_statistics'),
                path('errors/', affectation.view_errors, name='internship_affectation_errors'),
                path('generate/', affectation.run_affectation, name='internship_affectation_generate'),
                path('import/', affectation.import_affectations, name='internship_affectation_import'),
                path('sumup/', affectation.internship_affectation_sumup, name='internship_affectation_sumup'),
            ])),

            path('scores_encoding/', include([
                path('', score.scores_encoding, name='internship_scores_encoding'),
                path(
                    'edit/<str:student_registration_id>/<int:period_id>/<str:specialty_name>/',
                     score.score_detail_form,
                     name='internship_edit_score'
                 ),
                path('upload_scores/', score.upload_scores, name='internship_upload_scores'),
                path('upload_eval/', score.upload_eval, name='internship_upload_eval'),
                path('download/', score.download_scores, name='internship_download_scores'),
                path('download_summary/<int:student_id>', score.download_summary,
                     name='internship_download_summary'
                     ),
                path('mapping/save', score.save_mapping, name='save_internship_score_mapping'),
                path('ajax/save_score/', score.save_edited_score, name='save_edited_score'),
                path('ajax/delete_score/', score.delete_edited_score, name='delete_edited_score'),
                path('ajax/save_evaluation_status/', score.save_evaluation_status, name='save_evaluation_status'),
                path('ajax/save_evolution_score/', score.save_evolution_score, name='save_evolution_score'),
                path('ajax/delete_evolution_score/', score.delete_evolution_score, name='delete_evolution_score'),
                path('ajax/refresh_evolution_score/', score.refresh_evolution_score, name='refresh_evolution_score'),
                path('ajax/empty_score/', score.empty_score, name='empty_score'),
                re_path(r'^send_summary(?:/(?P<period_id>[0-9]+)/)?$', score.send_recap, name='send_summary'),
            ])),

            path('internship_evaluation/', include([
                path('', place_evaluation.internship_place_evaluation, name='place_evaluation'),
                path('results/', place_evaluation.internship_place_evaluation_results,
                     name='place_evaluation_results'),
                path('config/', place_evaluation.internship_place_evaluation_config,
                     name='place_evaluation_config'),
                path('export/', place_evaluation.export_place_evaluation_results,
                     name='export_place_evaluation_results'),
                path('new/', place_evaluation.internship_place_evaluation_item_new,
                     name='place_evaluation_new'),
                path('edit/<int:item_id>', place_evaluation.internship_place_evaluation_item_edit,
                     name='place_evaluation_edit'),
                path('delete/<int:item_id>', place_evaluation.internship_place_evaluation_item_delete,
                     name='place_evaluation_delete'),
                path('move_up/<int:item_id>', place_evaluation.internship_place_evaluation_item_move_up,
                     name='place_evaluation_item_move_up'),
                path('move_down/<int:item_id>', place_evaluation.internship_place_evaluation_item_move_down,
                     name='place_evaluation_item_move_down'),
            ])),
        ])),
    ])),
]
