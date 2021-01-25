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

from internship.api.serializers.period import PeriodSerializer
from internship.models.period import Period


class PeriodList(generics.ListAPIView):
    """
       Return a list of periods with optional filtering.
    """
    name = 'period-list'
    serializer_class = PeriodSerializer
    queryset = Period.objects.all()
    search_fields = (
        'name'
    )
    ordering_fields = (
        'date_start',
    )
    ordering = (
        'date_start',
    )  # Default ordering


class PeriodActiveList(generics.ListAPIView):
    """
       Return a list of active periods with optional filtering.
    """
    name = 'period-active-list'
    serializer_class = PeriodSerializer
    queryset = Period.active.all()
    search_fields = (
        'name'
    )
    ordering_fields = (
        'date_start',
    )
    ordering = (
        'date_start',
    )  # Default ordering


class PeriodActiveList(generics.ListAPIView):
    """
       Return a list of active periods with optional filtering.
    """
    name = 'period-active-list'
    serializer_class = PeriodSerializer
    queryset = Period.active.all()
    search_fields = (
        'name'
    )
    ordering_fields = (
        'date_start',
    )
    ordering = (
        'date_start',
    )  # Default ordering


class PeriodDetail(generics.RetrieveAPIView):
    """
        Return the detail of the period
    """
    name = 'period-detail'
    serializer_class = PeriodSerializer
    queryset = Period.objects.all()
    lookup_field = 'uuid'
