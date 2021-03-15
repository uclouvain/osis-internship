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
from rest_framework import serializers
from rest_framework.fields import UUIDField

from base.api.serializers.student import StudentSerializer
from internship.api.serializers.internship import InternshipSerializer
from internship.api.serializers.internship_score import InternshipScoreSerializer
from internship.api.serializers.period import PeriodSerializer
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat


class InternshipStudentAffectationSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='internship_api_v1:student-affectation-detail',
        lookup_field='uuid'
    )
    student = StudentSerializer(read_only=True)
    organization = UUIDField()
    speciality = UUIDField()
    internship = InternshipSerializer(read_only=True)
    period = PeriodSerializer(read_only=True)
    score = InternshipScoreSerializer(read_only=True)

    class Meta:
        model = InternshipStudentAffectationStat
        fields = (
            'url',
            'uuid',
            'student',
            'organization',
            'speciality',
            'period',
            'internship',
            'score'
        )
