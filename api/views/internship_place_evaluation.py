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
from django.http import HttpResponseNotFound
from rest_framework import generics

from internship.api.serializers.internship_place_evaluation import InternshipStudentPlaceEvaluationSerializer
from internship.models.internship_place_evaluation import PlaceEvaluation
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat


class InternshipStudentPlaceEvaluation(generics.RetrieveUpdateAPIView):
    """
       Return an internship student place evaluation
    """
    name = 'student-place-evaluation'
    serializer_class = InternshipStudentPlaceEvaluationSerializer
    queryset = PlaceEvaluation.objects.all()

    def get_object(self):
        try:
            return self.queryset.get(affectation__uuid=self.kwargs['affectation_uuid'])
        except PlaceEvaluation.DoesNotExist:
            try:
                affectation = InternshipStudentAffectationStat.objects.get(uuid=self.kwargs['affectation_uuid'])
                return self.queryset.create(affectation=affectation, evaluation={})
            except InternshipStudentAffectationStat.DoesNotExist:
                return HttpResponseNotFound()
