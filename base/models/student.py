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
from django.core.exceptions import ObjectDoesNotExist

class StudentAdmin(admin.ModelAdmin):
    list_display = ('person', 'registration_id', 'changed')
    fieldsets = ((None, {'fields': ('registration_id', 'person')}),)
    raw_id_fields = ('person', )
    search_fields = ['person__first_name', 'person__last_name']


class Student(models.Model):
    external_id     = models.CharField(max_length=100, blank=True, null=True)
    changed         = models.DateTimeField(null=True)
    registration_id = models.CharField(max_length=10)
    person          = models.ForeignKey('Person')

    def __str__(self):
        return u"%s (%s)" % (self.person, self.registration_id)


def find_by_person(a_person):
    try:
        student = Student.objects.get(person=a_person)
        return student
    except ObjectDoesNotExist:
        return None

def find_by_name(s_name) :
    return Student.objects.filter(person__last_name__icontains=s_name)

def find_by_registration_id_name(registration_id, s_name) :
    return Student.objects.filter(registration_id__icontains=s_noma, person__last_name__icontains=s_name)

def find_by_registration_id(registration_id):
    return Student.objects.filter(registration_id__icontains=registration_id)

def find_by_username_of_person(s_username):
    return Student.objects.get(person__user=s_username)
