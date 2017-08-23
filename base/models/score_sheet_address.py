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
from base.models.enums import offer_year_entity_type


class ScoreSheetAddressAdmin(admin.ModelAdmin):
    list_display = ('type',)
    fieldsets = ((None, {'fields': ('name', 'organization')}),)
    search_fields = ['type']


class ScoreSheetAddress(models.Model):
    # external_id = models.CharField(max_length=100, blank=True, null=True)
    # changed = models.DateTimeField(null=True, auto_now=True)
    offer_year_entity = models.ForeignKey('OfferYearEntity', blank=True, null=True)
    level = models.PositiveIntegerField(blank=True, null=True)

    location = models.CharField(max_length=255, blank=True, null=True)  # Address for scores cheets
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.ForeignKey('reference.Country', blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    fax = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(null=True, blank=True)

    @property
    def customized(self):
        return self.location and self.postal_code and self.city and not self.offer_year_entity and not self.entity_type

    def get_address(self):
        if not self.customized:
            address = entity_address.find_by_id(self.offer_year_entity_id)
            return address.get_address()

    def save(self, *args, **kwargs):
        if self.customized or (self.offer_year_entity and self.entity_type):
            super(ScoreSheetAddress, self).save(*args, **kwargs)
        else:
            raise Exception("Please set either offer_year_entity and level nor location, postal_code, city... but not all of them.")

    def __str__(self):
        return u"%s - %s - %s" % (self.offer_year, self.entity, self.type)
