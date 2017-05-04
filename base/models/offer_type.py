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
from django.db import models
from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin


class OfferTypeAdmin(SerializableModelAdmin):
    list_display = ('name', 'offer_year')
    fieldsets = ((None, {'fields': ('name', 'offer_year')}),)
    list_filter = ('name', 'offer_year')
    raw_id_fields = ('offer_year',)
    search_fields = ['name', 'offer_year']


class OfferType(SerializableModel):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=255)
    offer_year = models.ForeignKey('OfferYear')

    def __str__(self):
        return u"%s - %s" % (self.name, self.offer_year)


def find_by_academic_year(academic_yr):
    return OfferType.objects.filter(offer_year__academic_year=academic_yr).distinct('name').order_by('name')
