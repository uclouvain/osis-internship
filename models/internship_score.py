##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
import uuid as uuid
from django.contrib.admin import ModelAdmin
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Model

APD_NUMBER = 15
MIN_APDS = 5
MAX_APDS = 9


class InternshipScoreAdmin(ModelAdmin):
    score_fields = ['APD_{}'.format(index) for index in range(1, APD_NUMBER+1)]
    list_display = (
        'student', 'period', 'cohort',
        *score_fields, 'score', 'excused', 'reason', 'validated',
    )
    raw_id_fields = ('student_affectation',)
    list_filter = ('student_affectation__period__cohort', 'validated', 'student_affectation__speciality__name')
    search_fields = [
        'student_affectation__student__person__first_name',
        'student_affectation__student__person__last_name'
    ]
    list_select_related = (
        'student_affectation__period__cohort',
        'student_affectation__student__person',
    )


class InternshipScore(Model):

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)

    SCORE_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    )

    student_affectation = models.OneToOneField(
        'internship.InternshipStudentAffectationStat',
        on_delete=models.PROTECT,
        related_name='score',
        null=True
    )

    for index in range(1, APD_NUMBER+1):
        vars()['APD_{}'.format(index)] = models.CharField(
            max_length=1,
            choices=SCORE_CHOICES,
            null=True,
            blank=True,
        )
    score = models.IntegerField(null=True, blank=True)
    excused = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, null=True, blank=True)

    # TODO: import JSONField from models in Django 3
    comments = JSONField(default=dict, blank=True)
    objectives = JSONField(default=dict, blank=True)

    validated = models.BooleanField(default=False)
    student_presence = models.NullBooleanField()

    def __str__(self):
        return '{} - {}'.format(self.student_affectation, self.get_scores())

    def get_scores(self):
        return [vars(self)['APD_{}'.format(index)] for index in range(1, APD_NUMBER+1)]

    @property
    def student(self):
        return self.student_affectation.student if self.student_affectation else None

    @property
    def period(self):
        return self.student_affectation.period if self.student_affectation else None

    @property
    def cohort(self):
        return self.period.cohort if self.period else None
