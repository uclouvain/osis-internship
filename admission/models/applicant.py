##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid

from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from osis_common.models.serializable_model import SerializableModel


class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date', 'gender', 'activation_code')
    fieldsets = ((None, {'fields': ('last_name', 'first_name', 'birth_date', 'gender', 'language', 'nationality',
                                    'registration_id')}),)


class Applicant(SerializableModel):
    GENDER_CHOICES = (
        ('FEMALE', _('female')),
        ('MALE', _('male')))

    CIVIL_STATUS_CHOICES = (
        ('MARRIED', _('married')),
        ('SINGLE', _('single')),
        ('WIDOWED', _('widowed')),
        ('DIVORCED', _('divorced')),
        ('SEPARATED', _('separated')),
        ('COHABITANT', _('cohabitant')),
        ('UNKNOWN', _('unknown')))

    activation_code = models.UUIDField(default=uuid.uuid4, editable=False, blank=True, null=True)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    birth_place = models.CharField(max_length=255, blank=True, null=True)
    birth_country = models.ForeignKey('reference.Country', blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_CHOICES, default='UNKNOWN', blank=True,
                                    null=True)
    number_children = models.IntegerField(blank=True, null=True)
    spouse_name = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.ForeignKey('reference.Country', related_name='person_nationality', blank=True, null=True)
    national_id = models.CharField(max_length=25, blank=True, null=True)
    id_card_number = models.CharField(max_length=25, blank=True, null=True)
    passport_number = models.CharField(max_length=25, blank=True, null=True)
    phone_mobile = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    additional_email = models.EmailField(max_length=255, blank=True, null=True)
    registration_id = models.CharField(max_length=20, blank=True, null=True)
    last_academic_year = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=30, null=True, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)


    def __str__(self):
        return "{0} {1}".format(self.first_name, self.last_name)

