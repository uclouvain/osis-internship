##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from datetime import timedelta

from django.test import SimpleTestCase
from django.utils.datetime_safe import date
from django.utils.translation import gettext as _

from internship.templatetags.user_account import user_account_expiry


class TestUserAccountTag(SimpleTestCase):
    def test_should_expiry_date_less_than_today_use_danger_level(self):
        expiry_date = date.today() - timedelta(days=1)
        self.assertEqual(
            user_account_expiry(expiry_date),
            {'remaining': _('Expired'), 'level': 'danger', 'expiry_date': expiry_date}
        )

    def test_should_expiry_date_less_than_7_days_use_danger_level(self):
        expiry_date = date.today() + timedelta(days=6)
        self.assertEqual(
            user_account_expiry(expiry_date),
            {'remaining': _('{} day(s)').format(6), 'level': 'danger', 'expiry_date': expiry_date}
        )

    def test_should_expiry_date_less_than_3_months_use_warning_level(self):
        expiry_date = date.today() + timedelta(days=90)
        self.assertEqual(
            user_account_expiry(expiry_date),
            {'remaining': _('< 3 months'), 'level': 'warning', 'expiry_date': expiry_date}
        )

    def test_should_expiry_date_more_than_3_months_use_ok_level(self):
        expiry_date = date.today() + timedelta(days=120)
        self.assertEqual(
            user_account_expiry(expiry_date),
            {'remaining': _('> 3 months'), 'level': 'ok', 'expiry_date': expiry_date}
        )
