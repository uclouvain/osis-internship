##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from internship.api.serializers.internship_place_evaluation_item import InternshipPlaceEvaluationItemSerializer
from internship.models.internship_place_evaluation_item import PlaceEvaluationItem


class InternshipPlaceEvaluationItemList(generics.ListAPIView):
    """
       Return a list of internship place evaluation items with optional filtering.
    """
    name = 'student-place-evaluation-item-list'
    serializer_class = InternshipPlaceEvaluationItemSerializer
    queryset = PlaceEvaluationItem.objects.all()
    search_fields = (
        'cohort'
    )
    ordering_fields = (
        'order',
    )
    ordering = (
        'order',
    )  # Default ordering

    def get_queryset(self):
        return PlaceEvaluationItem.objects.all().filter(cohort__name=self.kwargs.get('cohort'), active=True)
