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


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'acronym', 'changed')
    fieldsets = ((None, {'fields': ('name', 'acronym', 'website', 'reference')}),)
    search_fields = ['acronym']


class Organization(models.Model):
    external_id = models.CharField(max_length=100, blank=True, null=True)
    changed     = models.DateTimeField(null=True)
    name        = models.CharField(max_length=255)
    acronym     = models.CharField(max_length=15)
    website     = models.CharField(max_length=255, blank=True, null=True)
    reference   = models.CharField(max_length=30, blank=True, null=True)

    def __str__(self):
        return self.name


def find_by_id(id):
    return Organization.objects.get(pk=id)


def find_by_acronym(acronym):
    return Organization.objects.filter(acronym__icontains=acronym)


def find_by_name(name):
    return Organization.objects.filter(name__icontains=name)


def find_by_acronym_name(acronym, name):
    return Organization.objects.filter(acronym__icontains=acronym, name__icontains=name)


def find_all():
    return Organization.objects.all().order_by('acronym')
