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
from base.models.academic_calendar import AcademicCalendar
from base.models.exception import FunctionAgrumentMissing, StartDateHigherThanEndDate

start_date = datetime.datetime.now()
end_date = start_date.replace(year=start_date.year + 1)


def create_academic_year():
    academic_yr = academic_year.AcademicYear(year=2016, start_date=start_date, end_date=end_date)
    academic_yr.save()
    return academic_yr


class AcademicCalendarFunctionArgs(TestCase):

    def setUp(self):
        self.academic_year = create_academic_year()

    def test_save_without_functions_args(self):
        ac_cal = AcademicCalendar(academic_year=self.academic_year,
                                  title="A calendar event",
                                  start_date=start_date,
                                  end_date=end_date)
        self.assertRaises(FunctionAgrumentMissing, ac_cal.save)


class AcademicCalendarStartEndDates(TestCase):

    def setUp(self):
        self.academic_year = create_academic_year()

    def test_start_date_higher_than_end_date(self):
        wrong_end_date = datetime.datetime.now()
        wrong_start_date = wrong_end_date.replace(year=start_date.year + 1)
        academic_cal = AcademicCalendar(academic_year=self.academic_year,
                                        title="A calendar event",
                                        start_date=wrong_start_date,
                                        end_date=wrong_end_date)
        self.assertRaises(StartDateHigherThanEndDate, academic_cal.save, functions=[])

    def test_start_date_equal_to_end_date(self):
        wrong_end_date = datetime.datetime.now()
        wrong_start_date = wrong_end_date
        academic_cal = AcademicCalendar(academic_year=self.academic_year,
                                        title="A calendar event",
                                        start_date=wrong_start_date,
                                        end_date=wrong_end_date)
        self.assertRaises(StartDateHigherThanEndDate, academic_cal.save, functions=[])