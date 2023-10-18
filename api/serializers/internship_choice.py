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
from rest_framework import serializers
from rest_framework.fields import UUIDField, CharField

from internship.api.serializers.internship_score import InternshipScoreListSerializer
from internship.api.serializers.internship_specialty import InternshipSpecialtySerializer
from internship.api.serializers.internship_student import InternshipStudentSerializer
from internship.api.serializers.organization import OrganizationSerializer
from internship.api.serializers.period import PeriodSerializer
from internship.models.internship_choice import InternshipChoice
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat


class InternshipChoiceSerializer(serializers.ModelSerializer):
    student = InternshipStudentSerializer(read_only=True)
    specialty = InternshipSpecialtySerializer(source='speciality', read_only=True)
    internship = serializers.CharField(read_only=True, source='internship.name')
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = InternshipChoice
        fields = (
            'uuid',
            'student',
            'organization',
            'internship',
            'specialty',
            'choice',
            'priority',
            'registered',
        )


class FirstChoiceCountSerializer(serializers.Serializer):

    reference = serializers.CharField(read_only=True, source='organization__reference')
    organization_name = serializers.CharField(read_only=True, source='organization__name')
    specialty = serializers.CharField(read_only=True, source='speciality__name')
    specialty_uuid = serializers.UUIDField(read_only=True, source='speciality__uuid')
    count = serializers.IntegerField(read_only=True)

