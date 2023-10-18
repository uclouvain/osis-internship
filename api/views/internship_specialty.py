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

from internship.api.serializers.internship_specialty import InternshipSpecialtySerializer
from internship.models.internship_speciality import InternshipSpeciality

from django_filters import rest_framework as filters


class SpecialtyFilter(filters.FilterSet):
    cohort_name = filters.CharFilter(field_name="cohort__name")
    selectable = filters.BooleanFilter(field_name="selectable")

    class Meta:
        model = InternshipSpeciality
        fields = ['cohort_name', 'selectable']


class InternshipSpecialtyList(generics.ListAPIView):
    """
       Return a list of specialties with optional filtering.
    """
    name = 'specialty-list'
    serializer_class = InternshipSpecialtySerializer
    queryset = InternshipSpeciality.objects.all().order_by('name')
    filterset_fields = (
        'cohort',
    )
    search_fields = (
        'name', 'acronym'
    )
    ordering_fields = (
        'cohort', 'acronym'
    )
    ordering = (
        'cohort',
    )  # Default ordering
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = SpecialtyFilter


class InternshipSpecialtyDetail(generics.RetrieveAPIView):
    """
        Return the detail of the specialty.
    """
    name = 'specialty-detail'
    serializer_class = InternshipSpecialtySerializer
    queryset = InternshipSpeciality.objects.all()
    lookup_field = 'uuid'
