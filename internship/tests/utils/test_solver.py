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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import unittest
from django.test import SimpleTestCase, TestCase
from base.tests.factories.student import StudentFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.speciality import SpecialityFactory
from internship.tests.factories.offer import OfferFactory
from internship.tests.models.test_internship_choice import create_internship_choice
from internship.utils.student_assignment.solver import Solver
from internship.models.internship_enrollment import InternshipEnrollment

class SolverTestCase(TestCase):
    def setUp(self):
        self.speciality = SpecialityFactory()
        self.internship = InternshipFactory(speciality=self.speciality)
        self.student = StudentFactory()
        self.organization = OrganizationFactory(cohort=self.internship.cohort)
        self.offer = OfferFactory(organization=self.organization, cohort=self.organization.cohort, speciality=self.speciality, internship=self.internship, selectable=True)

    def test_assigns_to_available_period(self):
        create_internship_choice(self.organization, self.student, self.speciality, self.internship, choice=1)
        enrollments = Solver().build_enrollments()
        expected_enrollment = InternshipEnrollment(student=self.student, offer=self.offer, internship=self.internship, period=self.period)
        self.assertContains(expected_enrollment, enrollments)

