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
from django.conf.urls import url

from internship.api.views.cohort import CohortList, CohortDetail
from internship.api.views.internship import InternshipList, InternshipDetail
from internship.api.views.internship_master import InternshipMasterList, InternshipMasterDetail
from internship.api.views.internship_specialty import InternshipSpecialtyList, InternshipSpecialtyDetail
from internship.api.views.internship_student_affectation_stat import InternshipStudentAffectationList, \
    InternshipStudentAffectationDetail
from internship.api.views.internship_student_information import InternshipStudentInformationList, \
    InternshipStudentInformationDetail
from internship.api.views.master_allocation import MasterAllocationList, MasterAllocationDetail
from internship.api.views.organization import OrganizationList, OrganizationDetail
from internship.api.views.period import PeriodList, PeriodDetail

app_name = "internship"
urlpatterns = [
    url(r'^masters/$', InternshipMasterList.as_view(), name=InternshipMasterList.name),
    url(r'^masters/(?P<uuid>[0-9a-f-]+)$', InternshipMasterDetail.as_view(), name=InternshipMasterDetail.name),

    url(r'^masters_allocations/$', MasterAllocationList.as_view(), name=MasterAllocationList.name),
    url(r'^masters_allocations/(?P<uuid>[0-9a-f-]+)$', MasterAllocationDetail.as_view(), name=MasterAllocationDetail.name),

    url(r'^specialties/$', InternshipSpecialtyList.as_view(), name=InternshipSpecialtyList.name),
    url(r'^specialties/(?P<uuid>[0-9a-f-]+)$', InternshipSpecialtyDetail.as_view(), name=InternshipSpecialtyDetail.name),

    url(r'^cohorts/$', CohortList.as_view(), name=CohortList.name),
    url(r'^cohorts/(?P<uuid>[0-9a-f-]+)$', CohortDetail.as_view(), name=CohortDetail.name),

    url(r'^organizations/$', OrganizationList.as_view(), name=OrganizationList.name),
    url(r'^organizations/(?P<uuid>[0-9a-f-]+)$', OrganizationDetail.as_view(), name=OrganizationDetail.name),

    url(r'^internships/$', InternshipList.as_view(), name=InternshipList.name),
    url(r'^internships/(?P<uuid>[0-9a-f-]+)$', InternshipDetail.as_view(), name=InternshipDetail.name),

    url(r'^students/$', InternshipStudentInformationList.as_view(), name=InternshipStudentInformationList.name),
    url(r'^students/(?P<uuid>[0-9a-f-]+)$', InternshipStudentInformationDetail.as_view(), name=InternshipStudentInformationDetail.name),

    url(r'^periods/$', PeriodList.as_view(), name=PeriodList.name),
    url(r'^periods/(?P<uuid>[0-9a-f-]+)$', PeriodDetail.as_view(), name=PeriodDetail.name),

    url(r'^students_affectations/$', InternshipStudentAffectationList.as_view(), name=InternshipStudentAffectationList.name),
    url(r'^students_affectations/(?P<uuid>[0-9a-f-]+)$', InternshipStudentAffectationDetail.as_view(), name=InternshipStudentAffectationDetail.name),
]
