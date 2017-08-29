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
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


class EntityAddressAdmin(admin.ModelAdmin):
    list_display = ('entity', 'label', 'location', 'postal_code', 'city', 'country')
    fieldsets = ((None, {'fields': ('entity', 'label', 'location', 'postal_code', 'city', 'country', 'phone', 'fax', 'email')}),)
    search_fields = ['entity__entityversion__acronym']


class EntityAddress(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    entity = models.OneToOneField('Entity')
    label = models.CharField(max_length=20)
    location = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=255)
    country = models.ForeignKey('reference.Country')
    phone = models.CharField(max_length=30, blank=True, null=True)
    fax = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Entity addresses"

    def __str__(self):
        return "{0} - {1}".format(self.id, self.external_id)


def find_by_id(pk):
    return EntityAddress.objects.filter(pk=pk)


def get_from_entity(entity):
    try:
        return EntityAddress.objects.get(entity=entity)
    except ObjectDoesNotExist:
        return None
