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
import datetime
from django.test import TestCase
from base.models import offer_year_calendar, offer_year
from base.tests.models import test_academic_calendar

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.offer_year_calendar import OfferYearCalendarFactory
from base.tests.factories.offer_year import OfferYearFactory


start_date = datetime.datetime.now()
end_date = start_date.replace(year=start_date.year + 1)
YEAR_CALENDAR = datetime.datetime.now().year


def create_offer_year_calendar(offer_yr, academic_year):
    academic_calendar = test_academic_calendar.create_academic_calendar(academic_year)
    return OfferYearCalendarFactory(offer_year=offer_yr, academic_calendar=academic_calendar)


def _create_academic_calendar_with_offer_year_calendars():
    an_academic_calendar = AcademicCalendarFactory.build(
        academic_year=AcademicYearFactory(year=datetime.datetime.now().year),
        title="Academic year {0} - {1}".format(start_date.year, start_date.year + 1),
        description="My offerYearCalendars are not customized (default value)",
        start_date=start_date,
        end_date=end_date)
    an_academic_calendar.save(functions=[offer_year_calendar.save_from_academic_calendar])
    return an_academic_calendar


class SaveFromAcademicCalendarTest(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory()  # Current academic year

    def test_case_none_parameter(self):
        with self.assertRaises(AttributeError):
            offer_year_calendar.save_from_academic_calendar(None)

    def test_case_not_yet_persistent_parameter(self):
        academic_calendar = AcademicCalendarFactory.build(academic_year=self.academic_year)
        with self.assertRaises(ValueError):
            offer_year_calendar.save_from_academic_calendar(academic_calendar)


class AcademicCalendarWithoutOfferYearCalendar(TestCase):
    def setUp(self):
        self.academic_year = AcademicYearFactory()  # Current academic year
        self.academic_calendar = AcademicCalendarFactory.build(academic_year=self.academic_year)
        self.academic_calendar.save(functions=[])

    def test_save_from_academic_calendar(self):
        self.assertEqual(len(offer_year_calendar.find_by_academic_calendar(self.academic_calendar)), 0)
        offer_year_calendar.save_from_academic_calendar(self.academic_calendar)
        self.assertEqual(len(offer_year_calendar.find_by_academic_calendar(self.academic_calendar)),
                         len(offer_year.find_by_academic_year(self.academic_calendar.academic_year)))


class AcademicCalendarWithOfferYearCalendarsCustomized(TestCase):
    def setUp(self):
        self.academic_calendar = _create_academic_calendar_with_offer_year_calendars()
        # Set offer year calendars customized
        offer_year_calendars = offer_year_calendar.OfferYearCalendar.objects.\
            filter(academic_calendar=self.academic_calendar)
        for off_cal in offer_year_calendars:
            off_cal.customized = True
            off_cal.start_date = datetime.datetime(2010, 4, 1, 16, 8, 18)
            off_cal.end_date = datetime.datetime(2011, 4, 1, 16, 8, 18)
            off_cal.save()

    def test_save_from_academic_calendar(self):
        offer_year_calendars = offer_year_calendar.OfferYearCalendar.objects.\
            filter(academic_calendar=self.academic_calendar, customized=True)
        for off_y_cal in offer_year_calendars:
            self.assertEquals(off_y_cal.start_date, datetime.datetime(2010, 4, 1, 16, 8, 18))
            self.assertNotEquals(off_y_cal.end_date, datetime.datetime(2011, 4, 1, 16, 8, 18))


class AcademicCalendarWithOfferYearCalendarsNotCustomized(TestCase):

    academic_calendar = None

    def setUp(self):
        self.academic_calendar = _create_academic_calendar_with_offer_year_calendars()
        self.set_offer_year_calendars_not_customized()

    def set_offer_year_calendars_not_customized(self):
        offer_year_calendars = offer_year_calendar.OfferYearCalendar.objects.\
            filter(academic_calendar=self.academic_calendar)
        for off_cal in offer_year_calendars:
            off_cal.customized = False
            off_cal.save()

    def test_save_from_academic_calendar(self):
        offer_year_calendars = offer_year_calendar.OfferYearCalendar.objects.\
            filter(academic_calendar=self.academic_calendar)
        for off_y_cal in offer_year_calendars:
            self.assertEquals(off_y_cal.start_date, start_date)
            self.assertEquals(off_y_cal.end_date, end_date)


class OfferYearCalendarsAttributesValidation(TestCase):

    def setUp(self):
        self.academic_year = AcademicYearFactory(year=YEAR_CALENDAR,
                                                 start_date=datetime.datetime(YEAR_CALENDAR, 9, 1),
                                                 end_date=datetime.datetime(YEAR_CALENDAR+1, 10, 30))
        self.academic_calendar = AcademicCalendarFactory.build(academic_year=self.academic_year,
                                                               start_date=datetime.datetime(YEAR_CALENDAR, 9, 1),
                                                               end_date=datetime.datetime(YEAR_CALENDAR+1, 10, 30))
        self.academic_calendar.save(functions=[])
        self.offer_year = OfferYearFactory(academic_year=self.academic_year)

    def test_end_date_lower_than_start_date(self):
        self.offer_year_calendar = OfferYearCalendarFactory.build(offer_year=self.offer_year,
                                                                  academic_calendar=self.academic_calendar)
        self.offer_year_calendar.start_date = datetime.datetime(YEAR_CALENDAR, 9, 1)
        self.offer_year_calendar.end_date = datetime.datetime(YEAR_CALENDAR, 8, 1)
        with self.assertRaises(AttributeError):
            self.offer_year_calendar.save()

    def test_end_date_greather_than_academic_calendar_end_date(self):
        self.offer_year_calendar = OfferYearCalendarFactory.build(offer_year=self.offer_year,
                                                                  academic_calendar=self.academic_calendar)
        self.offer_year_calendar.start_date = datetime.datetime(YEAR_CALENDAR, 9, 1)
        self.offer_year_calendar.end_date = self.academic_calendar.end_date + datetime.timedelta(days=2)
        with self.assertRaises(AttributeError):
            self.offer_year_calendar.save()

    def test_start_date_lower_than_academic_calendar_start_date(self):
        self.offer_year_calendar = OfferYearCalendarFactory.build(offer_year=self.offer_year,
                                                                  academic_calendar=self.academic_calendar)
        self.offer_year_calendar.end_date = datetime.datetime(YEAR_CALENDAR+2, 8, 1)
        self.offer_year_calendar.start_date = self.academic_calendar.start_date - datetime.timedelta(days=2)
        with self.assertRaises(AttributeError):
            self.offer_year_calendar.save()
