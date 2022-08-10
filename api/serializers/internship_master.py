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
from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from base.api.serializers.person import PersonDetailSerializer
from base.models.enums.person_source_type import INTERNSHIP
from base.models.person import Person
from internship.models.internship_master import InternshipMaster
from osis_common.utils.models import get_object_or_none


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
        )

    def create(self, *args, **kwargs):
        master = get_object_or_none(InternshipMaster, person__email=self.validated_data['person']['email'])
        if not master:
            email = self.validated_data['person'].pop('email')
            person, created = Person.objects.get_or_create(email=email, defaults={
                **self.validated_data['person'],
                'source': INTERNSHIP
            })
            master = InternshipMaster(person=person, civility=self.validated_data['civility'])
            master.save()
        return master

    def is_valid(self, *args, **kwargs):
        is_valid = super().is_valid(self)

        email = self.validated_data['person']['email']

        for subdomain in settings.INTERNAL_EMAIL_SUBDOMAINS:
            email_stripped_subdomain = email.replace(f"{subdomain}.", '')
            if subdomain in email and Person.objects.filter(email=email_stripped_subdomain).exists():
                raise ValidationError(
                    detail=_(
                        "A similar person with the following email address has been found: "
                        "<b>{}</b>. Please use this information instead."
                    ).format(email_stripped_subdomain)
                )

        return is_valid
