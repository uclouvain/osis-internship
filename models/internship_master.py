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
from django.db import models
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from internship.models.enums.civility import Civility
from internship.models.enums.gender import Gender
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class InternshipMasterAdmin(SerializableModelAdmin):
    list_display = ('first_name', 'last_name', 'civility')
    fieldsets = ((None, {'fields': ('first_name', 'last_name', 'civility', 'gender', 'email',
                                    'email_private', 'location', 'postal_code', 'city', 'country', 'phone',
                                    'phone_mobile', 'birth_date', 'start_activities')}),)


class InternshipMaster(SerializableModel):
    first_name = models.CharField(max_length=50, blank=True, null=True, db_index=True)
    last_name = models.CharField(max_length=50, db_index=True)
    civility = models.CharField(max_length=50, blank=True, null=True, choices=Civility.choices())
    gender = models.CharField(max_length=1, blank=True, null=True, choices=Gender.choices())
    email = models.EmailField(max_length=255, blank=True, null=True)
    email_private = models.EmailField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey(
        'reference.Country',
        blank=True, null=True,
        on_delete=models.CASCADE
    )
    phone = models.CharField(max_length=30, blank=True, null=True)
    phone_mobile = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    start_activities = models.DateField(blank=True, null=True)

    def clean(self):
        self.clean_birth_date()

    def clean_birth_date(self):
        if self.birth_date is not None and self.birth_date > timezone.now().date():
            raise ValidationError({"birth_date": _("Birth date must be on or before today's date.")}, code="invalid")

    def civility_acronym(self):
        if self.civility:
            return Civility.get_acronym(self.civility)
        else:
            return ""

    def __str__(self):
        return "{}, {}".format(self.last_name, self.first_name)


def get_by_id(master_id):
    try:
        return InternshipMaster.objects.get(pk=master_id)
    except ObjectDoesNotExist:
        return None
