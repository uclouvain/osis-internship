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
from .models import *
from core.models import Person

class InternshipEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('learning_unit_enrollment','organization', 'start_date', 'end_date')
    fieldsets = ((None, {'fields': ('learning_unit_enrollment','organization', 'start_date', 'end_date')}),)

admin.site.register(InternshipEnrollment, InternshipEnrollmentAdmin)

class PlaceAdmin(admin.ModelAdmin):
    list_display = ('number', 'name', 'address', 'postal_code', 'town', 'country', 'url')
    fieldsets = ((None, {'fields': ('number', 'name', 'address', 'postal_code', 'town', 'country', 'url')}),)

admin.site.register(Place, PlaceAdmin)

class StudentAdmin(admin.ModelAdmin):
    list_display = ('noma', 'annual_bloc', 'mail', 'address', 'postal_code', 'town', 'phone_number')
    fieldsets = ((None, {'fields': ('noma', 'annual_bloc', 'mail', 'address', 'postal_code', 'town', 'phone_number')}),)

admin.site.register(Student_, StudentAdmin)

class InternshipAdmin(admin.ModelAdmin):
    list_display = ('name', 'speciality', 'student_min', 'student_max')
    fieldsets = ((None, {'fields': ('name', 'speciality', 'student_min', 'student_max')}),)

admin.site.register(Internship, InternshipAdmin)

class PeriodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'date_start', 'date_end')
    fieldsets = ((None, {'fields': ('name', 'date_start', 'date_end')}),)

admin.site.register(Periode, PeriodeAdmin)

class InternshipMasterAdmin(admin.ModelAdmin):
    list_display = ('number', 'civility', 'type', 'speciality_id','speciality','mail')
    fieldsets = ((None, {'fields': ('number', 'civility', 'type', 'speciality_id','speciality','mail')}),)

admin.site.register(InternshipMaster, InternshipMasterAdmin)
