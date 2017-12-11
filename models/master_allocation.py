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
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class MasterAllocationAdmin(admin.ModelAdmin):
    list_display = ('master', 'organization', 'specialty')
    fieldsets = ((None, {'fields': ('master', 'organization', 'specialty')}),)
    raw_id_fields = ('master', 'organization', 'specialty')


class MasterAllocation(models.Model):
    CIVILITY_CHOICE = (('PROFESSOR', _('Professor')),
                       ('DOCTOR', _('Doctor')))
    TYPE_CHOICE = (('SPECIALIST', _('Specialist')),
                   ('GENERALIST', _('Generalist')))

    master = models.ForeignKey('internship.InternshipMaster')
    organization = models.ForeignKey('internship.Organization', blank=True, null=True)
    specialty = models.ForeignKey('internship.InternshipSpeciality', blank=True, null=True)

    def __str__(self):
        return "{}, {}".format(self.master.last_name, self.master.first_name)


def find_masters():
    return MasterAllocation.objects.all().select_related("organization")


def find_by_id(master_allocation_id):
    return MasterAllocation.objects.get(pk=master_allocation_id)


def find_by_master(a_master):
    return MasterAllocation.objects.filter(master=a_master)


def search(cohort, specialty, hospital):
    masters = MasterAllocation.objects.filter(organization__cohort=cohort)

    if specialty:
        masters = masters.filter(specialty=specialty)

    if hospital:
        masters = masters.filter(organization=hospital)

    if specialty or hospital:
        return masters
    else:
        return None
