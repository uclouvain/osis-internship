##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from django_filters import rest_framework as filters
from rest_framework import generics

from internship.api.serializers.internship_offer import InternshipOfferSerializer
from internship.models.internship_offer import InternshipOffer


class OfferFilter(filters.FilterSet):
    cohort_name = filters.CharFilter(field_name="cohort__name")
    specialty = filters.UUIDFilter(field_name="speciality__uuid")
    selectable = filters.BooleanFilter(field_name="selectable")

    class Meta:
        model = InternshipOffer
        fields = ['cohort_name', 'selectable', 'specialty']


class InternshipOfferList(generics.ListAPIView):
    """
       Return a list of internship offers with optional filtering.
    """
    name = 'internship-offer-list'
    serializer_class = InternshipOfferSerializer
    queryset = InternshipOffer.objects.all().select_related(
        'organization__cohort', 'cohort', 'speciality__cohort', 'organization__country',
    ).order_by('organization__reference', 'speciality__name')
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = OfferFilter
