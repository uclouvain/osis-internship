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

from django.db import models

from internship.models.enums.civility import Civility
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class InternshipCertifierAdmin(SerializableModelAdmin):
    list_display = ('person', 'civility', 'role')
    search_fields = ['person__last_name', 'person__first_name']
    fieldsets = (
        (
            None, {
                'fields': (
                    'person', 'civility', 'role', 'signature_b64'
                )
            }
        ),
    )


class InternshipCertifier(SerializableModel):
    person = models.ForeignKey('base.Person', blank=True, null=True, on_delete=models.CASCADE)
    civility = models.CharField(max_length=50, blank=True, null=True, choices=Civility.choices())
    role = models.CharField(max_length=100, blank=True, null=True)

    signature_b64 = models.TextField(blank=True, null=True)

    def civility_acronym(self):
        if self.civility:
            return Civility.get_acronym(self.civility)
        else:
            return ""
