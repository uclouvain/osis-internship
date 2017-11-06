##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test.testcases import TestCase
from base.tests.factories.student import StudentFactory
from internship.models import internship_student_affectation_stat
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialityFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories import internship_choice


class TestInternshipStudentAffectationStat(TestCase):
    def setUp(self):
        self.organization = OrganizationFactory()
        self.student = StudentFactory()
        self.specialty = SpecialityFactory()
        self.period = PeriodFactory()

    def test_build_without_choices(self):
        student_choices = []
        affectation = internship_student_affectation_stat.build(self.student, self.organization, self.specialty,
                                                                self.period, student_choices)

        self.assertEquals(affectation.cost, 10)
        self.assertEquals(affectation.choice, "I")

    def test_build_with_choices(self):
        cohort = CohortFactory()
        internship = InternshipFactory(cohort=cohort)
        self.choice = internship_choice.create_internship_choice(self.organization, self.student, self.specialty,
                                                                 internship=internship)
        student_choices = [self.choice,]
        affectation = internship_student_affectation_stat.build(self.student, self.organization, self.specialty,
                                                                self.period, student_choices)

        self.assertEquals(affectation.cost, 0)
        self.assertEquals(affectation.choice, self.choice.choice)
