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
from django.db.models import Subquery, OuterRef, CharField, F, Value, Count
from django.db.models.functions import Concat, Substr, Upper
from django.http import JsonResponse
from rest_framework import generics

from internship.api.serializers.internship_choice import InternshipChoiceSerializer, FirstChoiceCountSerializer
from internship.api.serializers.internship_student_affectation_stat import InternshipStudentAffectationSerializer, \
    InternshipPersonAffectationSerializer
from internship.models.internship import Internship
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.master_allocation import MasterAllocation


class InternshipChoiceList(generics.ListAPIView):
    """
       Return a list of internship choices with optional filtering.
    """
    name = 'internship-choice-list'
    serializer_class = InternshipChoiceSerializer
    queryset = InternshipChoice.objects.all().select_related(
        'organization', 'internship', 'student', 'speciality'
    ).order_by('organization__reference', 'speciality__name')

    def get_queryset(self, *args, **kwargs):
        has_criteria = False
        queryset = self.queryset.all()

        student_uuid = self.request.query_params.get('student_uuid')
        internship_uuid = self.request.query_params.get('internship_uuid')
        specialties_uuid = self.request.query_params.getlist('specialties_uuid')
        cohort_name = self.request.query_params.get('cohort_name')

        if student_uuid:
            queryset = queryset.filter(student__uuid=student_uuid)
            has_criteria = True

        if cohort_name:
            queryset = queryset.filter(internship__cohort__name=cohort_name)
            has_criteria = True

        if internship_uuid:
            queryset = queryset.filter(internship__uuid=internship_uuid)
            has_criteria = True

        if specialties_uuid:
            queryset = queryset.filter(speciality__uuid__in=specialties_uuid)
            has_criteria = True

        return queryset if has_criteria else []


class FirstChoiceOrganizationCount(generics.ListAPIView):
    name = 'first-choice-organization-count'
    serializer_class = FirstChoiceCountSerializer

    def get_queryset(self):
        return InternshipChoice.objects.filter(
            choice=1,
            organization__cohort__name=self.kwargs['cohort_name'],
        ).select_related('organization', 'internship', 'speciality').values(
            "organization__reference",
            "organization__name",
            "speciality__uuid",
            "speciality__name",
         ).annotate(count=Count("id")).order_by(
            'organization__reference', 'speciality__name'
        )
