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
from django.test import TestCase

from internship.forms.cohort import CohortForm
from internship.tests.factories.cohort import CohortFactory


class TestCohortForm(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.cohort = CohortFactory.build()

    def test_valid_form(self):
        data = {
            'name': self.cohort.name,
            'publication_start_date': self.cohort.publication_start_date.strftime('%Y-%m-%d'),
            'subscription_start_date': self.cohort.subscription_start_date.strftime('%Y-%m-%d'),
            'subscription_end_date': self.cohort.subscription_end_date.strftime('%Y-%m-%d'),
            'description': self.cohort.description,
        }
        form = CohortForm(data)
        self.assertTrue(form.is_valid())

    def test_start_before_end(self):
        data = {
            'name': self.cohort.name,
            'publication_start_date': self.cohort.publication_start_date.strftime('%Y-%m-%d'),
            'subscription_start_date': self.cohort.subscription_end_date.strftime('%Y-%m-%d'),
            'subscription_end_date': self.cohort.subscription_start_date.strftime('%Y-%m-%d'),
            'description': self.cohort.description,
        }
        form = CohortForm(data)
        self.assertFalse(form.is_valid())

    def test_publication_before_subscription_closed(self):
        data = {
            'name': self.cohort.name,
            'publication_start_date': self.cohort.subscription_end_date.strftime('%Y-%m-%d'),
            'subscription_start_date': self.cohort.subscription_start_date.strftime('%Y-%m-%d'),
            'subscription_end_date': self.cohort.publication_start_date.strftime('%Y-%m-%d'),
            'description': self.cohort.description,
        }
        form = CohortForm(data)
        self.assertFalse(form.is_valid())
