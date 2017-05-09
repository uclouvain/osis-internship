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
from django.db import models
from django.contrib import admin


class EntityAddressAdmin(admin.ModelAdmin):
    list_display = ('entity', 'label', 'location', 'postal_code', 'city', 'country', )
    search_fields = ['entity', 'label', 'location', 'postal_code', 'city', 'country']
    raw_id_fields = ('entity', )


class EntityAddress(models.Model):
    entity = models.ForeignKey('Entity')
    label = models.CharField(max_length=20, null=True)
    location = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    city = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)

    class Meta:
        verbose_name_plural = "entity addresses"


def search_by_entity(entity):
    return EntityAddress.objects.filter(entity=entity)
