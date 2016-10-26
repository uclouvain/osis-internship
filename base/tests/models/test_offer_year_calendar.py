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
from base.models import academic_year, offer_year_calendar, academic_calendar, offer_year


now = datetime.datetime.now()


class OfferYearCalendarTest(TestCase):
    fixtures = ['unit_test.json']

    @classmethod
    def setUpClass(cls):
        super(OfferYearCalendarTest, cls).setUpClass()

    def test_raise_if_parameter_not_conform_with_none_parameter(self):
        self.assertRaises(AttributeError, offer_year_calendar._raise_if_parameter_not_conform, *[None])

    def test_raise_if_parameter_not_conform_with_object_not_yet_persistent(self):
        academic_yr = academic_year.current_academic_year()
        academic_cal = academic_calendar.AcademicCalendar(academic_year=academic_yr,
                                                          title='A title',
                                                          description='A description',
                                                          start_date=now,
                                                          end_date=now)
        self.assertRaises(ValueError, offer_year_calendar._raise_if_parameter_not_conform, *[academic_cal])

    def test_create_from_academic_calendar(self):
        all_academic_cal_ids = offer_year_calendar.OfferYearCalendar.objects.values_list('academic_calendar__id',
                                                                                         flat=True)
        # Get an academic_calendar without linked OfferYearCalendar
        academic_cal = academic_calendar.AcademicCalendar.objects.exclude(id__in=all_academic_cal_ids)\
                                                                 .first()
        self.assertEqual(len(offer_year_calendar.find_by_academic_calendar(academic_cal)), 0)
        offer_year_calendar._create_from_academic_calendar(academic_cal)
        self.assertEqual(len(offer_year_calendar.find_by_academic_calendar(academic_cal)),
                         len(offer_year.find_by_academic_year(academic_cal.academic_year)))

    def test_update_dates(self):
        academic_cal = academic_calendar.AcademicCalendar.objects.filter(academic_year__year=2016) \
                                                                 .first()
        academic_cal.start_date = now
        academic_cal.end_date = now
        academic_cal.save()
        offer_year_calendars = offer_year_calendar.find_by_academic_calendar(academic_cal)
        for off_y_cal in offer_year_calendars:
            self.assertEquals(off_y_cal.start_date, now.date())
            if off_y_cal.customized:
                self.assertNotEquals(off_y_cal.end_date, now.date())
            else:
                self.assertEquals(off_y_cal.end_date, now.date())
