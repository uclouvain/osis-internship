##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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

from django.contrib.admin import ModelAdmin
from django.db import models
from django.db.models import Model


class PlaceEvaluationItemAdmin(ModelAdmin):
    list_display = ("student", "organization", "specialty", "period", "evaluation", "cohort")
    list_filter = ("affectation__organization__cohort",)
    search_fields = [
        "affectation__student__person__last_name",
        "affectation__student__person__first_name",
        "affectation__organization__name",
        "affectation__speciality__name",
        "affectation__period__name",
    ]
    raw_id_fields = ("affectation",)


class PlaceEvaluation(Model):

    affectation = models.ForeignKey('internship.InternshipStudentAffectationStat', on_delete=models.CASCADE, null=True)
    evaluation = models.JSONField(null=True)

    @property
    def student(self):
        return self.affectation.student

    @property
    def organization(self):
        return self.affectation.organization

    @property
    def specialty(self):
        return self.affectation.speciality

    @property
    def period(self):
        return self.affectation.period

    @property
    def cohort(self):
        return self.affectation.organization.cohort
