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
from distutils.util import strtobool

from django.db.models import Q
from rest_framework import generics

from internship.api.serializers.internship_student_affectation_stat import InternshipStudentAffectationSerializer
from internship.models.internship_score import InternshipScore, APD_NUMBER
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
        qs = InternshipStudentAffectationStat.objects.select_related('organization', 'speciality').filter(
            speciality__uuid=specialty_uuid, organization__uuid=organization_uuid
        )
        with_score = bool(strtobool(self.request.query_params.get('with_score')))
        period = self.request.query_params.get('period')
        if period:
            qs = qs.filter(period__name=period)
        if with_score:
            qs = self._filter_affectations_with_score(qs)
        return qs

    def _filter_affectations_with_score(self, qs):
        has_at_least_one_apd_evaluated = Q()
        for index in range(1, APD_NUMBER + 1):
            has_at_least_one_apd_evaluated |= Q(**{'APD_{}__isnull'.format(index): False})
        scores = InternshipScore.objects.filter(
            student__pk__in=qs.values('student_id'),
            period__pk__in=qs.values('period_id'),
        ).filter(has_at_least_one_apd_evaluated)
        students_with_scores = scores.values_list('student_id')
        qs = qs.filter(student_id__in=students_with_scores)
        return qs


class InternshipStudentAffectationDetail(generics.RetrieveAPIView):
    """
        Return the detail of the student affectation
    """
    name = 'student-affectation-detail'
    serializer_class = InternshipStudentAffectationSerializer
    queryset = InternshipStudentAffectationStat.objects.all()
    lookup_field = 'uuid'
