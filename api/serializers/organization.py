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
from internship.models.organization import Organization
from reference.api.serializers.country import CountrySerializer


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='internship_api_v1:organization-detail',
        lookup_field='uuid'
    )
    country = serializers.CharField(read_only=True, source='country.name')
    cohort = CohortSerializer()

    class Meta:
        model = Organization
        fields = [
            'url',
            'uuid',
            'name',
            'acronym',
            'website',
            'reference',
            'phone',
            'location',
            'postal_code',
            'city',
            'country',
            'cohort',
        ]


class OfferOrganizationSerializer(OrganizationSerializer):
    cohort = serializers.CharField(read_only=True, source='cohort.name')

    class Meta(OrganizationSerializer.Meta):
        fields = [field for field in OrganizationSerializer.Meta.fields if field != 'cohort']
