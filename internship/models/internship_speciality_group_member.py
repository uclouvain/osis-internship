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
from django.contrib import admin
from django.db import models


class InternshipSpecialityGroupMemberAdmin(admin.ModelAdmin):
    list_display = ('group', 'speciality')
    fieldsets = ((None, {'fields': ('group', 'speciality')}),)
    raw_id_fields = ('group', 'speciality')


class InternshipSpecialityGroupMember(models.Model):
    speciality = models.ForeignKey('internship.InternshipSpeciality')
    group = models.ForeignKey('internship.InternshipSpecialityGroup')

    def __str__(self):
        return u"%s - %s" % (self.speciality.name, self.group.name)


def search_by_group_name(group_name):
    return InternshipSpecialityGroupMember.objects.filter(group__name=group_name)


def find_by_speciality(speciality):
    return InternshipSpecialityGroupMember.objects.filter(speciality=speciality)\
        .order_by('speciality__order_postion')


def find_distinct_specialities_by_groups(groups):
    return InternshipSpecialityGroupMember.objects.filter(group__in=groups).distinct('speciality')
