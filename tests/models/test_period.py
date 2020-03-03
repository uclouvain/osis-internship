##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import date

from dateutil.relativedelta import relativedelta
from django.test import TestCase

from internship.tests.factories.period import PeriodFactory


def create_period(name="P1", cohort=None):
    return PeriodFactory(name=name, cohort=cohort)


class PeriodFactoryTestCase(TestCase):
    def test_dates(self):
        period = PeriodFactory()
        self.assertLess(period.date_start, period.date_end)

    def test_period_is_active(self):
        delta = relativedelta(days=1)
        period = PeriodFactory(date_start=date.today()-delta, date_end=date.today()+delta)
        self.assertTrue(period.is_active)

