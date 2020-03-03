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
from django.db import models

from osis_common.models.serializable_model import SerializableModel, SerializableModelAdmin

APD_NUMBER = 15


class InternshipScoreAdmin(SerializableModelAdmin):
    score_fields = ['APD_{}'.format(index) for index in range(1, APD_NUMBER+1)]
    list_display = ('student', 'period', *score_fields, 'score')
    raw_id_fields = ('student',)
    list_filter = ('cohort',)
    search_fields = ['student__person__first_name', 'student__person__last_name']


class InternshipScore(SerializableModel):

    SCORE_CHOICES = (
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D')
    )

    student = models.ForeignKey('base.student', on_delete=models.PROTECT)
    period = models.ForeignKey('internship.period', on_delete=models.PROTECT)
    cohort = models.ForeignKey('internship.cohort', on_delete=models.PROTECT)
    for index in range(1, APD_NUMBER+1):
        vars()['APD_{}'.format(index)] = models.CharField(
            max_length=1,
            choices=SCORE_CHOICES,
            null=True,
            blank=True,
        )
    score = models.IntegerField(null=True, blank=True)
    excused = models.BooleanField(default=False)

    def __str__(self):
        return '{} - {} - {}'.format(self.student, self.period, self.get_scores())

    def get_scores(self):
        return [vars(self)['APD_{}'.format(index)] for index in range(1, APD_NUMBER+1)]
