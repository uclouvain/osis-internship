##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.contrib import admin
from base.models import entity_address
from django.db import models
from assessments.models.enums import score_sheet_address_choices
from django.core.exceptions import ObjectDoesNotExist


class ScoreSheetAddressAdmin(admin.ModelAdmin):
    list_display = ('type',)
    fieldsets = ((None, {'fields': ('name', 'organization')}),)
    search_fields = ['type']


class ScoreSheetAddress(models.Model):
    offer_year = models.OneToOneField('base.OfferYear')
    # Info to find the address
    entity_address_choice = models.CharField(max_length=50, blank=True, null=True, choices=score_sheet_address_choices.CHOICES)
    # Address fields
    location = models.CharField(max_length=255, blank=True, null=True)  # Address for scores cheets
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    fax = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)

    @property
    def customized(self):
        return self.location and self.postal_code and self.city and not self.entity_address_choice

    def get_offer_year_type(self):
        if self.entity_address_choice:
            if score_sheet_address_choices.ENTITY_MANAGEMENT in self.entity_address_choice:
                return score_sheet_address_choices.ENTITY_MANAGEMENT
            else:
                return score_sheet_address_choices.ENTITY_ADMINISTRATION
        return None

    # def get_address(self):
    #     if self.customized:
    #         self._init_attrs(self)
    #     else:
    #         entity = offer_year_entity.get_from_offer_year_and_type(self.offer_year, self.get_offer_year_type())
    #         address = entity_address.find_by_id(entity)
    #         version = entity_version.get_last_version(entity)
    #         address.recipient = '{} - {}'.format(version.acronym, version.title)
    #         self._init_attrs(address)

    def save(self, *args, **kwargs):
        if self.customized or self.entity_address_choice:
            super(ScoreSheetAddress, self).save(*args, **kwargs)
        else:
            raise Exception("Please set either entity_address_choice nor location, postal_code, city... but not all of them.")

    def __str__(self):
        return u"%s - %s - %s" % (self.offer_year, self.entity, self.type)


def get_from_offer_year(off_year):
    try:
        return ScoreSheetAddress.objects.get(offer_year=off_year)
    except ObjectDoesNotExist:
        return None