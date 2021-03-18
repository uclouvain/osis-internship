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
from rest_framework import serializers

from base.models.student import Student
from internship.models.internship_score import APD_NUMBER, InternshipScore


def _apd_fields():
    return ['APD_{}'.format(index) for index in range(1, APD_NUMBER + 1)]


class StudentSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(read_only=True, source='person.first_name')
    last_name = serializers.CharField(read_only=True, source='person.last_name')

    class Meta:
        model = Student
        fields = ['uuid', 'first_name', 'last_name']
        depth = 1


class InternshipScoreSerializer(serializers.HyperlinkedModelSerializer):
    student = StudentSerializer()
    period = serializers.CharField(read_only=True, source='period.name')
    cohort = serializers.CharField(read_only=True, source='cohort.name')

    class Meta:
        model = InternshipScore
        fields = (
            'uuid',
            'student',
            'period',
            'score',
            'cohort',
            'comments',
            'objectives',
            'validated',
            *_apd_fields()
        )


class InternshipScorePutSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = InternshipScore
        fields = (
            'uuid',
            'score',
            'comments',
            'objectives',
            'validated',
            *_apd_fields()
        )
