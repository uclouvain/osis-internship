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
from datetime import timedelta

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.utils import timezone

from base.tests.factories.student import StudentFactory
from internship.business.assignment import difference, Assignment
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.factories.offer import OfferFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory


class AssignmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        self.user.user_permissions.add(permission)
        self.client.force_login(self.user)

        self.cohort = CohortFactory()
        self.assignment = Assignment(self.cohort)

class ListUtilsTestCase(TestCase):
    def test_difference_non_empty_lists(self):
        first_list = [1,2,3,4,5]
        second_list = [4,5]
        expected = [1,2,3]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_second_list(self):
        first_list = [1,2,3,4,5]
        second_list = []
        expected = [1,2,3,4,5]
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_first_list(self):
        first_list = []
        second_list = [1,2]
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_empty_lists(self):
        first_list = []
        second_list = []
        expected = []
        self.assertEqual(expected, difference(first_list, second_list))

    def test_difference_with_list_without_common_elements(self):
        first_list = [1,2,3,4]
        second_list = [5,6]
        expected = [1,2,3,4]
        self.assertEqual(expected, difference(first_list, second_list))