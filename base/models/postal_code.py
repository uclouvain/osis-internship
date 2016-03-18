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
from base.models import country


class PostalCodeAdmin(admin.ModelAdmin):
    list_display = ('place', 'code', 'country', 'admin1', 'admin2', 'admin3')
    fieldsets = (
    (None, {'fields': ('place', 'code', 'country', 'admin1', 'admin2', 'admin3')}),)
    ordering = ('country','place')
    search_fields = ['place','code','country']

class PostalCode(models.Model):

    place   = models.CharField(max_length=2)
    code    = models.CharField(max_length=80)
    country = models.ForeignKey(country.Country, on_delete=models.CASCADE)
    admin1  = models.CharField(max_length=1, blank=True, null=True)
    admin2  = models.CharField(max_length=3, blank=True, null=True)
    admin3  = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return self.place