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

from django.test import TestCase

from base.tests.factories.student import StudentFactory
from internship.business.scores import InternshipScoreRules
from internship.models.internship_score import APD_NUMBER
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.score import ScoreFactory


class InternshipScoreRulesTest(TestCase):
    def setUp(self) -> None:
        self.cohort = CohortFactory()
        self.student = StudentFactory()
        self.period = PeriodFactory(cohort=self.cohort)
        self.internship_score = ScoreFactory(
            student_affectation__student=self.student,
            student_affectation__period=self.period,
        )

    def test_student_fulfill_requirements(self):
        for index in [index for index in range(0, APD_NUMBER)]:
            vars(self.internship_score)['APD_{}'.format(index+1)] = 'D'
        self.student.scores = [(self.period, self.internship_score.get_scores())]
        self.assertTrue(InternshipScoreRules.student_has_fulfilled_requirements(self.student))

    def test_student_does_not_fulfill_requirements(self):
        self.internship_score.APD_1 = 'A'
        self.student.scores = [(self.period, self.internship_score.get_scores())]
        self.assertFalse(InternshipScoreRules.student_has_fulfilled_requirements(self.student))

    def test_student_except_apd_fulfill_requirements(self):
        for index in [index for index in range(0, APD_NUMBER)]:
            if index+1 not in InternshipScoreRules.EXCEPT_APDS:
                vars(self.internship_score)['APD_{}'.format(index + 1)] = 'D'
            else:
                vars(self.internship_score)['APD_{}'.format(index + 1)] = 'B'
        self.student.scores = [(self.period, self.internship_score.get_scores())]
        self.assertTrue(InternshipScoreRules.student_has_fulfilled_requirements(self.student))
