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

from internship.api.views.cohort import CohortList
from internship.api.views.internship import InternshipList
from internship.api.views.internship_master import InternshipMasterList
from internship.api.views.internship_specialty import InternshipSpecialtyList
from internship.api.views.internship_student_affectation_stat import InternshipStudentAffectationList
from internship.api.views.internship_student_information import InternshipStudentInformationList
from internship.api.views.master_allocation import MasterAllocationList
from internship.api.views.organization import OrganizationList
from internship.api.views.period import PeriodList

app_name = "internship"
urlpatterns = [
    url(r'^masters/$', InternshipMasterList.as_view(), name=InternshipMasterList.name),
    url(r'^masters_allocations/$', MasterAllocationList.as_view(), name=MasterAllocationList.name),
    url(r'^specialties/$', InternshipSpecialtyList.as_view(), name=InternshipSpecialtyList.name),
    url(r'^cohorts/$', CohortList.as_view(), name=CohortList.name),
    url(r'^organizations/$', OrganizationList.as_view(), name=OrganizationList.name),
    url(r'^internships/$', InternshipList.as_view(), name=InternshipList.name),
    url(r'^students/$', InternshipStudentInformationList.as_view(), name=InternshipStudentInformationList.name),
    url(r'^periods/$', PeriodList.as_view(), name=PeriodList.name),
    url(r'^students_affectations/$', InternshipStudentAffectationList.as_view(), name=InternshipStudentAffectationList.name),
]
