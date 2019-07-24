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


class InternshipScoreMappingAdmin(SerializableModelAdmin):
    list_display = ('period', 'apd', 'score_A', 'score_B', 'score_C', 'score_D')
    list_filter = ('period', 'cohort')


class InternshipScoreMapping(SerializableModel):

    period = models.ForeignKey('internship.period', on_delete=models.PROTECT)
    apd = models.IntegerField()

    score_A = models.IntegerField(default=0)
    score_B = models.IntegerField(default=0)
    score_C = models.IntegerField(default=0)
    score_D = models.IntegerField(default=0)

    cohort = models.ForeignKey('internship.cohort', on_delete=models.PROTECT)

    def __str__(self):
        return '{} - {} - {}'.format(self.period, self.apd, self.score_A, self.score_B, self.score_C, self.score_D)
