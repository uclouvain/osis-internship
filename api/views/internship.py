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
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django_filters import rest_framework as filters
from rest_framework import generics

from internship.api.serializers.internship import InternshipSerializer
from internship.models.internship import Internship


class InternshipFilter(filters.FilterSet):
    cohort_name = filters.CharFilter(field_name="cohort__name")

    class Meta:
        model = Internship
        fields = ['cohort_name']


class InternshipList(generics.ListAPIView):
    """
       Return a list of internships with optional filtering.
    """
    name = 'internship-list'
    serializer_class = InternshipSerializer
    queryset = Internship.objects.all().order_by('speciality__name', 'name').annotate(
        periods=ArrayAgg('internshipmodalityperiod__period__name',
            ordering='internshipmodalityperiod__period__name',
            distinct=True,
            filter=Q(internshipmodalityperiod__period__name__isnull=False),
        ),
        apds=ArrayAgg(
            'internshipmodalityapd__apd',
            distinct=True,
            filter=Q(internshipmodalityapd__apd__isnull=False),
        ),
    )
    search_fields = (
        'name', 'speciality'
    )
    ordering_fields = (
        'position', 'name', 'length_in_periods'
    )
    ordering = (
        'name'
    )  # Default ordering
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = InternshipFilter


class InternshipDetail(generics.RetrieveAPIView):
    """
        Return the detail of the internship.
    """
    name = 'internship-detail'
    serializer_class = InternshipSerializer
    queryset = Internship.objects.all().annotate(
        periods=ArrayAgg('internshipmodalityperiod__period__name',
            ordering='internshipmodalityperiod__period__name',
            distinct=True,
            filter=Q(internshipmodalityperiod__period__name__isnull=False)
        ),
        apds=ArrayAgg(
            'internshipmodalityapd__apd',
            distinct=True,
            filter=Q(internshipmodalityapd__apd__isnull=False)
        ),
    )
    lookup_field = 'uuid'
