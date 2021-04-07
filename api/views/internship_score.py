##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
from rest_framework import generics, status
from rest_framework.response import Response

from internship.api.serializers.internship_score import InternshipScoreDetailSerializer, InternshipScorePutSerializer
from internship.models.internship_score import InternshipScore
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat


class InternshipScoreCreateRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """
       Return an internship score detail
    """
    name = 'score-detail'
    lookup_field = 'uuid'
    queryset = InternshipScore.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return InternshipScorePutSerializer
        return InternshipScoreDetailSerializer

    def get_object(self):
        try:
            return InternshipScore.objects.get(student_affectation__uuid=self.kwargs['affectation_uuid'])
        except InternshipScore.DoesNotExist:
            affectation = InternshipStudentAffectationStat.objects.get(
                uuid=self.kwargs['affectation_uuid']
            )
            if affectation:
                return InternshipScore.objects.create(student_affectation=affectation)


class ValidateInternshipScore(generics.GenericAPIView):
    """
      Validate an internship score
    """
    name = 'score-validation'
    lookup_field = 'student_affectation__uuid'
    lookup_url_kwarg = 'affectation'
    queryset = InternshipScore.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        object = self.get_object()
        object.validated = True
        object.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

