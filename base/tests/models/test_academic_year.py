##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
import datetime
from django.test import TestCase
from base.models import academic_year


now = datetime.datetime.now()


class MultipleAcademicYearTest(TestCase):
    def setUp(self):
        academic_yr = academic_year.AcademicYear(year=(now.year - 1),
                                                 start_date=datetime.datetime(now.year - 1, now.month, 15),
                                                 end_date=datetime.datetime(now.year, now.month, 28))
        academic_yr.save()
        academic_yr = academic_year.AcademicYear(year=now.year,
                                                 start_date=datetime.datetime(now.year, now.month, 15),
                                                 end_date=datetime.datetime(now.year + 1, now.month, 28))
        academic_yr.save()

    def test_current_academic_years(self):
        academic_yrs = academic_year.current_academic_years()
        self.assertEqual(len(academic_yrs), 2)

    def test_current_academic_year(self):
        academic_yr = academic_year.current_academic_year()
        self.assertEqual(academic_yr.year, now.year - 1)

    def test_starting_academic_year(self):
        academic_yr = academic_year.starting_academic_year()
        self.assertEqual(academic_yr.year, now.year)


class SingleAcademicYearTest(TestCase):
    def setUp(self):
        academic_yr = academic_year.AcademicYear(year=now.year,
                                                 start_date=datetime.datetime(now.year, now.month, 15),
                                                 end_date=datetime.datetime(now.year + 1, now.month, 28))
        academic_yr.save()

    def test_starting_equalto_current(self):
        academic_yr = academic_year.starting_academic_year()
        self.assertEqual(academic_yr.year, now.year)


class InexistingAcademicYearTest(TestCase):
    def test_inexisting_academic_year(self):
        self.assertEqual(academic_year.current_academic_year(), None)
        self.assertEqual(academic_year.starting_academic_year(), None)


class PeriodAcademicYearTest(TestCase):
    def test_future_academic_year(self):
        academic_yr = academic_year.AcademicYear(year=(now.year + 1),
                                                 start_date=datetime.datetime(now.year + 1, now.month, 15),
                                                 end_date=datetime.datetime(now.year + 2, now.month, 28))
        self.assertRaises(AttributeError, academic_yr.save)

    def test_start_date_year(self):
        academic_yr = academic_year.AcademicYear(year=(now.year + 1),
                                                 start_date=datetime.datetime(now.year + 2, now.month, 15),
                                                 end_date=datetime.datetime(now.year + 3, now.month, 28))
        self.assertRaises(AttributeError, academic_yr.save)

    def test_start_date_before_end_date(self):
        academic_yr = academic_year.AcademicYear(year=(now.year + 1),
                                                 start_date=datetime.datetime(now.year + 1, now.month, 15),
                                                 end_date=datetime.datetime(now.year + 1, now.month, 15))
        self.assertRaises(AttributeError, academic_yr.save)
