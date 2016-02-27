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

from base.models.learning_unit_enrollment import LearningUnitEnrollment


class LearningUnitYear(models.Model):
    external_id    = models.CharField(max_length=100, blank=True, null=True)
    changed        = models.DateTimeField(null=True)
    acronym        = models.CharField(max_length=15)
    title          = models.CharField(max_length=255)
    credits        = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    decimal_scores = models.BooleanField(default=False)
    academic_year  = models.ForeignKey('AcademicYear')
    learning_unit  = models.ForeignKey('LearningUnit')

    def __str__(self):
        return u"%s - %s" % (self.academic_year,self.learning_unit)


def find_offer_enrollments_by_learning_unit_year(learning_unit_year_id):
    learning_unit_enrollment_list= LearningUnitEnrollment.objects.filter(learning_unit_year=learning_unit_year_id)
    offer_list = []
    for lue in learning_unit_enrollment_list:
        offer_list.append(lue.offer_enrollment)
    return offer_list


def find_learning_unit_years_by_academic_year(academic_year):
    return LearningUnitYear.objects.filter(academic_year=int(academic_year))


def find_learning_unit_year_by_id(learning_unit_id) :
    return LearningUnitYear.objects.get(pk=learning_unit_id)