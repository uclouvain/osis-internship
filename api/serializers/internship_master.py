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

from base.api.serializers.person import PersonDetailSerializer
from base.models.enums.person_source_type import INTERNSHIP
from base.models.person import Person
from internship.models.internship_master import InternshipMaster


class InternshipMasterSerializer(serializers.HyperlinkedModelSerializer):
    person = PersonDetailSerializer()
    url = serializers.HyperlinkedIdentityField(
        view_name='internship_api_v1:master-detail',
        lookup_field='uuid'
    )

    class Meta:
        model = InternshipMaster
        fields = (
            'url',
            'uuid',
            'person',
            'civility',
            'user_account_status',
            'role'
        )

    def create(self, *args, **kwargs):
        master = _master_exists(self.initial_data['email'])
        if not master:
            person = Person(**self.initial_data['person'], source=INTERNSHIP)
            person.save()
            master = InternshipMaster(
                person=person,
                role=self.initial_data['role'],
                civility=self.initial_data['civility']
            )
            master.save()
        return master


def _master_exists(email):
    try:
        return InternshipMaster.objects.get(person__email=email)
    except InternshipMaster.DoesNotExist:
        return None
