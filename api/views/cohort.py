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
from rest_framework import generics

from internship.api.serializers.cohort import CohortSerializer
from internship.models.cohort import Cohort


class CohortList(generics.ListAPIView):
    """
       Return a list of cohorts with optional filtering.
    """
    name = 'cohort-list'
    serializer_class = CohortSerializer
    queryset = Cohort.objects.all()
    search_fields = (
        'name'
    )
    ordering_fields = (
        'publication_start_date',
    )
    ordering = (
        'publication_start_date',
    )  # Default ordering


class CohortDetail(generics.RetrieveAPIView):
    """
        Return the detail of the cohort.
    """
    name = 'cohort-detail'
    serializer_class = CohortSerializer
    queryset = Cohort.objects.all()
    lookup_field = 'uuid'
