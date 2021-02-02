##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from internship.models.enums.civility import Civility
from internship.models.enums.user_account_status import UserAccountStatus
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class InternshipMasterAdmin(SerializableModelAdmin):
    list_display = ('person', 'civility')
    fieldsets = (
        (
            None, {
                'fields': (
                    'person', 'civility', 'email_private', 'email_additional', 'start_activities', 'user_account_status'
                )
            }
        ),
    )


class InternshipMaster(SerializableModel):
    person = models.ForeignKey('base.Person', blank=True, null=True, on_delete=models.CASCADE)

    email_private = models.EmailField(max_length=255, blank=True, null=True, verbose_name='Private email')
    email_additional = models.CharField(max_length=255, blank=True, null=True, verbose_name='Additional email')
    civility = models.CharField(max_length=50, blank=True, null=True, choices=Civility.choices())

    start_activities = models.DateField(blank=True, null=True)

    user_account_status = models.CharField(
        max_length=50,
        choices=UserAccountStatus.choices(),
        default=UserAccountStatus.INACTIVE.value,
    )

    def civility_acronym(self):
        if self.civility:
            return Civility.get_acronym(self.civility)
        else:
            return ""

    def __str__(self):
        try:
            return "{}, {}".format(self.person.last_name, self.person.first_name)
        except AttributeError:
            return "-"


def get_by_id(master_id):
    try:
        return InternshipMaster.objects.get(pk=master_id)
    except ObjectDoesNotExist:
        return None
