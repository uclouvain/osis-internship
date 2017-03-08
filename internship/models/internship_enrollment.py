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


class InternshipEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'internship_offer', 'place', 'period')
    fieldsets = ((None, {'fields': ('student', 'internship_offer', 'place', 'period')}),)
    raw_id_fields = ('student', 'internship_offer', 'place', 'period')


class InternshipEnrollment(models.Model):
    student = models.ForeignKey('base.student')
    internship_offer = models.ForeignKey('internship.InternshipOffer')
    place = models.ForeignKey('internship.Organization')
    period = models.ForeignKey('internship.Period')

    def __str__(self):
        return u"%s - %s" % (self.student, self.internship_offer.title)


def search(**kwargs):
    kwargs = {k: v for k, v in kwargs.items() if v}
    return InternshipEnrollment.objects.filter(**kwargs)\
                                       .select_related("student", "internship_offer", "place", "period")


def search_by_student_and_internship_id(student, internship_id):
    return InternshipEnrollment.objects.filter(student=student, internship_offer_id=internship_id)


def find_by_student(student):
    return InternshipEnrollment.objects.filter(student=student)