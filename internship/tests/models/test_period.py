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

from internship.models import period as mdl_period
import datetime
from django.test import TestCase


def create_period(name="P1"):
    period = mdl_period.Period(name=name, date_start=datetime.date.today(), date_end=datetime.date.today())
    period.save()
    return period


class TestFindByName(TestCase):
    def test_find(self):
        period_1 = create_period(name="P1")
        period_2 = create_period(name="P5")

        self.assertEqual(period_1, mdl_period.find_by_name("P1"))
        self.assertEqual(period_2, mdl_period.find_by_name("P5"))

        self.assertFalse(mdl_period.find_by_name("P4"))
