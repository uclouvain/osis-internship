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
from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.utils import timezone

from internship.forms import organization_form

from reference.models.country import Country


class TestOrganizationForm(TestCase):

    def test_valid_form(self):
        belgium = Country.find_by_uuid("ae40df86-04e9-4e9b-8dca-0c1e26b1476d")
        data = {
            "reference":"00",
            "name": "test",
            "website": "test.be",
            "location": "location",
            "postal_code": "1348",
            "city": "city",
            "country": belgium,
        }
        form = organization_form.OrganizationForm(data)
        self.assertTrue(form.is_valid())

    def test_duplicate_sequence(self):
        data = {
            "name": "test",
            "report_period": 1,
            "report_noma": 1
        }
        form = organization_form.OrganizationForm(data)
        self.assertFalse(form.is_valid())
