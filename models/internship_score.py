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
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Model, JSONField
from django.utils.translation import gettext_lazy as _

APD_NUMBER = 15
MIN_APDS = 5
MAX_APDS = 9




class InternshipScoreAdmin(ModelAdmin):
    score_fields = [f'APD_{index}' for index in range(1, APD_NUMBER+1)]
    list_display = (
        'student', 'period', 'cohort',
        *score_fields, 'score', 'behavior_score', 'competency_score', 'calculated_global_score',
        'excused', 'reason', 'validated',
    )
    raw_id_fields = ('student_affectation', 'validated_by')
    list_filter = (
        'student_affectation__period__cohort',
        'student_affectation__period__is_preconcours',
        'validated',
        'student_affectation__speciality__name'
    )
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
        on_delete=models.CASCADE,
        related_name='score',
        null=True,
        verbose_name=_('Student Affectation'),
    )

    for index in range(1, APD_NUMBER+1):
        vars()['APD_{}'.format(index)] = models.CharField(
            max_length=1,
            choices=SCORE_CHOICES,
            null=True,
            blank=True,
        )
    score = models.IntegerField(null=True, blank=True, verbose_name=_('Score'))
    excused = models.BooleanField(default=False, verbose_name=_('Excused'))
    reason = models.CharField(max_length=255, null=True, blank=True, verbose_name=_('Reason'))

    comments = JSONField(default=dict, blank=True, verbose_name=_('Comments'))
    objectives = JSONField(default=dict, blank=True, verbose_name=_('Objectives'))
    preconcours_evaluation_detail = JSONField(default=dict, blank=True, verbose_name=_('Preconcours Evaluation Detail'))

    validated = models.BooleanField(default=False, verbose_name=_('Validated'))
    validated_by = models.ForeignKey(
        'base.Person', blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('Validated by')
    )

    student_presence = models.BooleanField(null=True, verbose_name=_('Student presence'))

    behavior_score = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ],
        verbose_name=_("Behavior score")
    )
    competency_score = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(20)
        ],
        verbose_name=_("Skill score")
    )

    def __str__(self):
        return f'{self.student_affectation} - {self.get_scores()}'

    def get_scores(self):
        return [vars(self)[f'APD_{index}'] for index in range(1, APD_NUMBER+1)]

    @property
    def student(self):
        return self.student_affectation.student if self.student_affectation else None

    @property
    def period(self):
        return self.student_affectation.period if self.student_affectation else None

    @property
    def cohort(self):
        return self.period.cohort if self.period else None

    @property
    def is_preconcours(self):
        return self.period.is_preconcours if self.period else False

    @property
    def calculated_global_score(self):
        """Calculate global score as average of behavior and competency scores for preconcours periods"""
        if not self.is_preconcours or not all([self.behavior_score, self.competency_score]):
            return None
        return (self.behavior_score + self.competency_score) / 2
