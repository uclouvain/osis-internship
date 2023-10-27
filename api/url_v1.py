##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.urls import path

from internship.api.views.cohort import CohortList, CohortDetail, CohortOpenForSelection
from internship.api.views.internship import InternshipList, InternshipDetail
from internship.api.views.internship_choice import InternshipChoiceList, FirstChoiceOrganizationCount, \
    InternshipSaveChoice, InternshipDeleteChoices
from internship.api.views.internship_master import InternshipMasterActivateAccount, InternshipMasterUpdateDetail, \
    InternshipMasterAllocationListCreate, InternshipMasterListCreate
from internship.api.views.internship_offer import InternshipOfferList
from internship.api.views.internship_place_evaluation import InternshipStudentPlaceEvaluation
from internship.api.views.internship_place_evaluation_item import InternshipPlaceEvaluationItemList
from internship.api.views.internship_score import InternshipScoreCreateRetrieveUpdate, ValidateInternshipScore
from internship.api.views.internship_specialty import InternshipSpecialtyList, InternshipSpecialtyDetail
from internship.api.views.internship_student_affectation_stat import InternshipStudentAffectationList, \
    InternshipStudentAffectationDetail, InternshipStudentAffectationStats, InternshipPersonAffectationList
from internship.api.views.internship_student_information import InternshipStudentInformationList, \
    InternshipStudentInformationDetail
from internship.api.views.master_allocation import MasterAllocationUpdateDeleteDetail, MasterAllocationListCreate
from internship.api.views.organization import OrganizationList, OrganizationDetail
from internship.api.views.period import PeriodList, PeriodDetail

app_name = "internship"
urlpatterns = [
    path('masters', InternshipMasterListCreate.as_view(), name=InternshipMasterListCreate.name),
    path('masters/<uuid:uuid>/', InternshipMasterUpdateDetail.as_view(),
         name=InternshipMasterUpdateDetail.name),
    path('masters/<uuid:uuid>/activate_account/', InternshipMasterActivateAccount.as_view(),
         name=InternshipMasterActivateAccount.name),
    path('masters/<uuid:uuid>/allocations', InternshipMasterAllocationListCreate.as_view(),
         name=InternshipMasterAllocationListCreate.name),

    path('masters_allocations/<uuid:uuid>/', MasterAllocationUpdateDeleteDetail.as_view(),
         name=MasterAllocationUpdateDeleteDetail.name),
    path('masters_allocations', MasterAllocationListCreate.as_view(), name=MasterAllocationListCreate.name),

    path('specialties', InternshipSpecialtyList.as_view(), name=InternshipSpecialtyList.name),
    path('specialties/<uuid:uuid>/', InternshipSpecialtyDetail.as_view(), name=InternshipSpecialtyDetail.name),

    path('cohorts', CohortList.as_view(), name=CohortList.name),
    path('cohorts/<str:name>/', CohortDetail.as_view(), name=CohortDetail.name),
    path('cohorts/<str:name>/is_open_for_selection', CohortOpenForSelection.as_view(),
         name=CohortOpenForSelection.name),

    path('organizations', OrganizationList.as_view(), name=OrganizationList.name),
    path('organizations/<uuid:uuid>/', OrganizationDetail.as_view(), name=OrganizationDetail.name),

    path('internships', InternshipList.as_view(), name=InternshipList.name),
    path('internships/<uuid:uuid>/', InternshipDetail.as_view(), name=InternshipDetail.name),

    path('students', InternshipStudentInformationList.as_view(), name=InternshipStudentInformationList.name),
    path('students/<uuid:uuid>/', InternshipStudentInformationDetail.as_view(),
         name=InternshipStudentInformationDetail.name),

    path('periods', PeriodList.as_view(), name=PeriodList.name),
    path('periods/<uuid:uuid>/', PeriodDetail.as_view(), name=PeriodDetail.name),

    path('students_affectations/<uuid:specialty_uuid>/<uuid:organization_uuid>',
         InternshipStudentAffectationList.as_view(), name=InternshipStudentAffectationList.name),
    path('students_affectations/<uuid:specialty_uuid>/<uuid:organization_uuid>/stats/',
         InternshipStudentAffectationStats.as_view(), name=InternshipStudentAffectationStats.name),
    path('students_affectations/<uuid:affectation_uuid>/', InternshipStudentAffectationDetail.as_view(),
         name=InternshipStudentAffectationDetail.name),
    path('person_affectations/<str:cohort_name>/<uuid:person_uuid>/', InternshipPersonAffectationList.as_view(),
         name=InternshipPersonAffectationList.name),

    path('scores/<uuid:affectation_uuid>/', InternshipScoreCreateRetrieveUpdate.as_view(),
         name=InternshipScoreCreateRetrieveUpdate.name),
    path('scores/<uuid:affectation>/validate/', ValidateInternshipScore.as_view(),
         name=ValidateInternshipScore.name),
    path('place_evaluation_items/<str:cohort>/', InternshipPlaceEvaluationItemList.as_view(),
         name=InternshipPlaceEvaluationItemList.name),
    path('place_evaluation/<uuid:affectation_uuid>/', InternshipStudentPlaceEvaluation.as_view(),
         name=InternshipStudentPlaceEvaluation.name),

    path('choices/', InternshipChoiceList.as_view(), name=InternshipChoiceList.name),
    path('save_choice/<uuid:internship_uuid>/', InternshipSaveChoice.as_view(), name=InternshipSaveChoice.name),
    path('delete_choices/<uuid:internship_uuid>/',
         InternshipDeleteChoices.as_view(), name=InternshipDeleteChoices.name),
    path('first_choices_count/<str:cohort_name>/',
         FirstChoiceOrganizationCount.as_view(), name=FirstChoiceOrganizationCount.name),
    path('offers/', InternshipOfferList.as_view(), name=InternshipOfferList.name),

]
