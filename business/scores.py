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
from internship.models.internship_score import APD_NUMBER


class InternshipScoreRules:
    NA_GRADE = 'E'
    NORMAL_GRADES = ['C', 'D']
    EXCEPT_APDS = [8, 14, 15]
    EXCEPT_GRADES = NORMAL_GRADES + ['B']

    @classmethod
    def get_valid_grades(cls, index):
        return cls.EXCEPT_GRADES if index in cls.get_except_apds_indices() else cls.NORMAL_GRADES

    @classmethod
    def get_except_apds_indices(cls):
        return [x - 1 for x in cls.EXCEPT_APDS]

    @classmethod
    def is_score_valid(cls, index, score):
        return score in cls.get_valid_grades(index)

    @classmethod
    def student_has_fulfilled_requirements(cls, student):
        # student fulfill requirements when he has at least 'C' for each APD
        if not student.scores:
            return False
        return cls._filter_fulfilled_apd_indices(student)

    @classmethod
    def _filter_fulfilled_apd_indices(cls, student):
        # remove iteratively apd from list when score is valid
        apd_indices = [index for index in range(0, APD_NUMBER)]
        for period, scores, period_aff_index in student.scores:
            if not apd_indices:
                break
            for apd, score in enumerate(scores):
                if cls._apd_can_be_removed(apd, apd_indices, score):
                    apd_indices.remove(apd)
        return not apd_indices

    @classmethod
    def _apd_can_be_removed(cls, apd, apd_indices, score):
        return apd in apd_indices and score and cls.is_score_valid(apd, score)
