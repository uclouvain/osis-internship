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


class InternshipChoice(models.Model):
    student             = models.ForeignKey('base.Student')
    organization        = models.ForeignKey('internship.Organization')
    speciality          = models.ForeignKey('internship.InternshipSpeciality',null=True)
    choice              = models.IntegerField()
    internship_choice   = models.IntegerField(default=0)
    priority            = models.BooleanField()

    @staticmethod
    def find_by_all_student():
        all = InternshipChoice.objects.all().distinct('student').select_related("student","organization","speciality")
        return all

    @staticmethod
    def find_by_student(s_student):
        internships = InternshipChoice.objects.filter(student = s_student).select_related("student","organization","speciality").order_by('choice')
        return internships

    @staticmethod
    def find_by_student_desc(s_student):
        internships = InternshipChoice.objects.filter(student = s_student).select_related("student","organization","speciality").order_by('-choice')
        return internships

    @staticmethod
    def search(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipChoice.objects.filter(**kwargs).select_related("student","organization","speciality").order_by('choice')
        return queryset

    @staticmethod
    def search_other_choices(**kwargs):
        kwargs = {k: v for k, v in kwargs.items() if v}
        queryset = InternshipChoice.objects.filter(**kwargs).select_related("student","organization","speciality").order_by('choice')
        queryset = queryset.exclude(choice=1)
        return queryset
