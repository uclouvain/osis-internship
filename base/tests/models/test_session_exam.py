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
from base.models import session_exam
from base.tests.models import test_offer_year, test_learning_unit_year, test_academic_calendar
from base.models import academic_year, session_exam, offer_year_calendar
from django.test import TestCase


def create_session_exam(number_session, learning_unit_year, offer_year_calendar):
    a_session_exam = session_exam.SessionExam(number_session=number_session,
                                              learning_unit_year=learning_unit_year,
                                              offer_year_calendar=offer_year_calendar)
    a_session_exam.save()
    return a_session_exam

class IsInsideScoreEncoding(TestCase):

    def setUp(self):
        self.academic_year = academic_year.AcademicYear(year=1900,
                                                        start_date= datetime.datetime(1900, 1, 1),
                                                        end_date=datetime.datetime(1900, 12, 28))
        self.academic_year.save()

        #Create offer year calendar
        self.offer_year_calendar = \
            offer_year_calendar.OfferYearCalendar(offer_year=test_offer_year.create_offer_year('DROI1BA',
                                                                                               'Bachelor in law',
                                                                                               self.academic_year),
                                                  academic_calendar=test_academic_calendar.create_academic_calendar(
                                                                    self.academic_year,
                                                                    start_date=datetime.datetime(1900, 1, 1),
                                                                    end_date=datetime.datetime(1900, 12, 28))
                                                  )
        self.offer_year_calendar.save()

        self.learning_unit_year = test_learning_unit_year.create_learning_unit_year("LDROI1004", "Juridic law courses", self.academic_year)
        create_session_exam(number_session=1, learning_unit_year= self.learning_unit_year, offer_year_calendar=self.offer_year_calendar)

    def test_is_inside_score_encoding(self):
        is_inside=session_exam.is_inside_score_encoding(date=datetime.datetime(1900, 2, 10)) #2 february 1900
        self.assertTrue(is_inside)

    def test_is_not_inside_score_encoding_below(self):
        is_inside = session_exam.is_inside_score_encoding(date=datetime.datetime(1899, 12, 30))  # 30 decembre 1899
        self.assertFalse(is_inside)

    def test_is_not_inside_score_encoding_upper(self):
        is_inside = session_exam.is_inside_score_encoding(date=datetime.datetime(1900, 12, 29))  # 29 decembre 1900
        self.assertFalse(is_inside)



class GetLatestSessionExam(TestCase):

    def setUp(self):
        self.academic_year = academic_year.AcademicYear(year=1901,
                                                        start_date=datetime.datetime(1901, 1, 1),
                                                        end_date=datetime.datetime(1901, 12, 28))
        self.academic_year.save()

        #Create offer year calendar [1 January 1901 to 28 Juny 1901]
        self.offer_year_calendar = \
            offer_year_calendar.OfferYearCalendar(offer_year=test_offer_year.create_offer_year('DROI1BA',
                                                                                               'Bachelor in law',
                                                                                               self.academic_year),
                                                  academic_calendar=test_academic_calendar.create_academic_calendar(
                                                      self.academic_year,
                                                      start_date=datetime.datetime(1901, 1, 1),
                                                      end_date=datetime.datetime(1901, 6, 28))
                                                  )
        self.offer_year_calendar.save()

        #Create offer year calendar [29 Juny 1901 to 30 December 1901]
        self.offer_year_calendar_2 = \
            offer_year_calendar.OfferYearCalendar(offer_year=test_offer_year.create_offer_year('DROI1BA',
                                                                                               'Bachelor in law',
                                                                                               self.academic_year),
                                                  academic_calendar=test_academic_calendar.create_academic_calendar(
                                                      self.academic_year,
                                                      start_date=datetime.datetime(1901, 6, 29),
                                                      end_date=datetime.datetime(1901, 12, 30))
                                                  )
        self.offer_year_calendar_2.save()

        self.learning_unit_year = test_learning_unit_year.create_learning_unit_year("LDROI1004", "Juridic law courses",
                                                                                    self.academic_year)
        self.first_session = create_session_exam(number_session=1, learning_unit_year=self.learning_unit_year,
                            offer_year_calendar=self.offer_year_calendar)
        self.second_session = create_session_exam(number_session=2, learning_unit_year=self.learning_unit_year,
                            offer_year_calendar=self.offer_year_calendar_2)


    def test_get_none_session_exam(self):
        latest = session_exam.get_latest_session_exam(date=datetime.datetime(1901, 1, 2))  # 2 January 1901
        self.assertIsNone(latest)

    def test_get_first_session(self):
        latest = session_exam.get_latest_session_exam(date=datetime.datetime(1901, 6, 30))  # 30 Juny 1901
        self.assertEqual(latest, self.first_session)

    def test_second_session(self):
        latest = session_exam.get_latest_session_exam(date=datetime.datetime(1902, 1, 1))  # 1 January 1902
        self.assertEqual(latest, self.second_session)