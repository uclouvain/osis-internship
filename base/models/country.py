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
from django.utils.translation import ugettext_lazy as _
from base.models.supported_languages import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE
from base.models import continent
from base.models import currency

class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso_code', 'nationality', 'eu', 'dialing_code', 'cref_code', 'currency', 'continent')
    fieldsets = (
    (None, {'fields': ('iso_code', 'name', 'nationality', 'eu', 'dialing_code', 'cref_code', 'currency', 'continent')}),)
    ordering = ('name',)
    search_fields = ['name']

class Country(models.Model):
    EU_COUNTRY = (('T', _('True')),
                  ('F', _('False')))

    iso_code      = models.CharField(max_length=2, unique=True)
    name         = models.CharField(max_length=80, unique=True)
    nationality  = models.CharField(max_length=80, null=True)
    eu           = models.CharField(max_length=1, choices=EU_COUNTRY)
    dialing_code = models.CharField(max_length=3)
    cref_code    = models.CharField(max_length=3, null=True)
    currency     = models.ForeignKey(currency.Currency, null=True, on_delete=models.CASCADE)
    continent    = models.ForeignKey(continent.Continent, on_delete=models.CASCADE)

    def __str__(self):
        return self.name