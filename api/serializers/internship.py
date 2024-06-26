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

from internship.api.serializers.cohort import CohortSerializer
from internship.api.serializers.internship_specialty import InternshipSpecialtySerializer
from internship.models.internship import Internship


class InternshipSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='internship_api_v1:internship-detail',
        lookup_field='uuid'
    )
    cohort = CohortSerializer()
    speciality = InternshipSpecialtySerializer()

    periods = serializers.ListField()
    apds = serializers.ListField()

    class Meta:
        model = Internship
        fields = (
            'url',
            'uuid',
            'name',
            'speciality',
            'cohort',
            'length_in_periods',
            'position',
            'periods',
            'apds',
        )
