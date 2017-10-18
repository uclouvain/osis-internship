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
from internship.utils.period_utils import *
from internship.tests.factories.period import PeriodFactory
from django.test import TestCase

class PeriodUtilsTestCase(TestCase):
    def setUp(self):
        self.p1 = PeriodFactory.build(name="P1", id=1)
        self.p2 = PeriodFactory.build(name="P2", id=2)
        self.p3 = PeriodFactory.build(name="P3", id=3)
        self.p4 = PeriodFactory.build(name="P4", id=4)
        self.p5 = PeriodFactory.build(name="P5", id=5)

    def test_1_consecutive_periods(self):
        periods = [self.p1, self.p2, self.p3, self.p4]
        expected = [[self.p1], [self.p2], [self.p3], [self.p4]]
        self.assertEqual(expected, list(group_periods_by_consecutives(periods)))

    def test_2_consecutive_periods(self):
        periods = [self.p1, self.p2, self.p3, self.p4]
        expected = [[self.p1, self.p2], [self.p2, self.p3], [self.p3, self.p4]]
        self.assertEqual(expected, list(group_periods_by_consecutives(periods, length=2)))

    def test_2_consecutive_periods_in_complicated_list(self):
        periods = [self.p2, self.p4, self.p5]
        expected = [[self.p4, self.p5]]
        self.assertEqual(expected, list(group_periods_by_consecutives(periods, length=2)))

    def test_2_consecutive_periods_in_other_complicated_list(self):
        periods = [self.p1, self.p2, self.p5]
        expected = [[self.p1, self.p2]]
        self.assertEqual(expected, list(group_periods_by_consecutives(periods, length=2)))

    def test_3_consecutive_periods(self):
        periods = [self.p1, self.p2, self.p3, self.p4, self.p5]
        expected = [[self.p1, self.p2, self.p3], [self.p2, self.p3, self.p4], [self.p3, self.p4, self.p5]]
        self.assertEqual(expected, list(group_periods_by_consecutives(periods, length=3)))

    def test_4_consecutive_periods(self):
        periods = [self.p1, self.p2, self.p3, self.p4, self.p5]
        expected = [[self.p1, self.p2, self.p3, self.p4], [self.p2, self.p3, self.p4, self.p5]]
        self.assertEqual(expected, list(group_periods_by_consecutives(periods, length=4)))

    def test_map_period_ids(self):
        periods = [self.p1, self.p2]
        expected = [self.p1.id, self.p2.id]
        self.assertEqual(expected, map_period_ids(periods))
