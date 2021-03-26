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

from internship.api.serializers.internship_master import InternshipMasterSerializer
from internship.api.serializers.internship_specialty import InternshipSpecialtySerializer
from internship.api.serializers.organization import OrganizationSerializer
from internship.models.enums.role import Role
from internship.models.internship_master import InternshipMaster
from internship.models.internship_speciality import InternshipSpeciality
from internship.models.master_allocation import MasterAllocation
from internship.models.organization import Organization


class MasterAllocationSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='internship_api_v1:master-allocation-detail',
        lookup_field='uuid'
    )
    master = InternshipMasterSerializer()
    organization = OrganizationSerializer()
    specialty = InternshipSpecialtySerializer()

    class Meta:
        model = MasterAllocation
        fields = (
            'url',
            'uuid',
            'master',
            'organization',
            'specialty',
            'role'
        )

    def create(self, *args, **kwargs):
        master = InternshipMaster.objects.get(uuid=self.validated_data['master']['uuid'])
        organization = Organization.objects.get(uuid=self.validated_data['organization']['uuid'])
        specialty = InternshipSpeciality.objects.get(uuid=self.validated_data['specialty']['uuid'])
        allocation = MasterAllocation(
            master=master,
            organization=organization,
            specialty=specialty,
            role=Role.DELEGATE.name
        )
        allocation.save()
        return allocation
