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

from django.http import JsonResponse
from rest_framework import generics

from internship.api.serializers.internship_student_affectation_stat import InternshipStudentAffectationSerializer
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat


class InternshipStudentAffectationList(generics.ListAPIView):
    """
       Return a list of internship student affectations with optional filtering.
    """
    name = 'student-affectation-list'
    serializer_class = InternshipStudentAffectationSerializer
    queryset = InternshipStudentAffectationStat.objects.all()
    search_fields = (
        # search by student person
    )
    ordering_fields = (
        'period__name',
    )
    ordering = (
        'period__name',
    )  # Default ordering

    def get_queryset(self):
        specialty_uuid = self.kwargs.get('specialty_uuid')
        organization_uuid = self.kwargs.get('organization_uuid')
        qs = InternshipStudentAffectationStat.objects.select_related(
            'student__person', 'score', 'organization', 'speciality', 'period__cohort', 'internship'
        ).filter(
            speciality__uuid=specialty_uuid, organization__uuid=organization_uuid
        )
        period = self.request.query_params.get('period')

        if period and period != "all":
            qs = qs.filter(period__name=period)

        return qs


class InternshipStudentAffectationDetail(generics.RetrieveAPIView):
    """
        Return the detail of the student affectation
    """
    name = 'student-affectation-detail'
    serializer_class = InternshipStudentAffectationSerializer
    queryset = InternshipStudentAffectationStat.objects.all()
    lookup_field = 'uuid'


class InternshipStudentAffectationStats(generics.RetrieveAPIView):
    """
        Return the total and encoded amount of students affectations for given organization and specialty
    """
    name = 'student-affectation-stats'

    def get(self, request, *args, **kwargs):
        specialty_uuid = self.kwargs['specialty_uuid']
        organization_uuid = self.kwargs['organization_uuid']

        qs = InternshipStudentAffectationStat.objects.filter(
            speciality__uuid=specialty_uuid, organization__uuid=organization_uuid
        )
        total_affectations_count = qs.count()

        validated_scores_count = qs.filter(score__validated=True).count()

        return JsonResponse({'total_count': total_affectations_count, 'validated_count': validated_scores_count})
