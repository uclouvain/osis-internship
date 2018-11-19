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
from django.db.models import Q
from django.contrib import admin
from internship.models.internship_master import InternshipMaster


class MasterAllocationAdmin(admin.ModelAdmin):
    list_display = ('master', 'organization', 'specialty', 'cohort')
    fieldsets = ((None, {'fields': ('master', 'organization', 'specialty')}),)
    raw_id_fields = ('master', 'organization', 'specialty')
    list_filter = ('organization__cohort', 'specialty__cohort')


class MasterAllocation(models.Model):
    master = models.ForeignKey('internship.InternshipMaster')
    organization = models.ForeignKey('internship.Organization', blank=True, null=True)
    specialty = models.ForeignKey('internship.InternshipSpeciality', blank=True, null=True)

    def cohort(self):
        return self.specialty.cohort if self.specialty else (self.organization.cohort if self.organization else None)

    def save(self, *args, **kwargs):
        existing = MasterAllocation.objects.filter(master=self.master,
                                                   organization=self.organization,
                                                   specialty=self.specialty)
        if not existing:
            super(MasterAllocation, self).save(*args, **kwargs)

    def __str__(self):
        return "{} - {} - {}".format(self.master, self.organization, self.specialty)


def find_by_master(cohort, a_master):
    return find_by_cohort(cohort).filter(master=a_master)


def find_unallocated_masters():
    allocated_masters = MasterAllocation.objects.values("pk").distinct()
    return InternshipMaster.objects.exclude(id__in=(list([a['pk'] for a in allocated_masters])))\
                                   .order_by('last_name', 'first_name')


def search(cohort, specialty, hospital):
    masters = find_by_cohort(cohort)

    if specialty:
        masters = masters.filter(specialty=specialty)

    if hospital:
        masters = masters.filter(organization=hospital)

    if specialty or hospital:
        return masters.order_by("master__last_name", "master__first_name")
    else:
        return masters\
            .filter(specialty__isnull=False, organization__isnull=False)\
            .order_by("master__last_name", "master__first_name")


def clean_allocations(cohort, master):
    find_by_master(cohort, master).delete()


def find_by_cohort(cohort_from):
    return MasterAllocation.objects.filter(Q(organization__cohort=cohort_from) | Q(specialty__cohort=cohort_from))
