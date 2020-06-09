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
from django.template.defaulttags import register

from internship.business.scores import InternshipScoreRules
from internship.models.internship_score import InternshipScore


@register.filter()
def is_valid(grade, index):
    if grade == InternshipScoreRules.NA_GRADE:
        return True
    return InternshipScoreRules.is_score_valid(index, grade)


@register.simple_tag
def is_apd_validated(cohort, student, apd):
    apd_grades = InternshipScore.objects.filter(
        cohort=cohort, student__person=student.person
    ).values_list('APD_{}'.format(apd), flat=True)
    valid_grades = InternshipScoreRules.get_valid_grades(apd-1)
    return bool(set(apd_grades).intersection(valid_grades))
