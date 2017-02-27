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
                                                        end_date= datetime.datetime(1900, 12, 28))
        self.academic_year.save()
        offer_year = test_offer_year.create_offer_year('DROI1BA', 'Bachelor in law', self.academic_year)

        #Create offer year calendar
        self.offer_year_calendar = \
            offer_year_calendar.OfferYearCalendar(offer_year=offer_year,
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
