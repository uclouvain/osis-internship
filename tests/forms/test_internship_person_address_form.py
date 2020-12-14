##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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

from base.models.enums.person_source_type import BASE, INTERNSHIP
from base.tests.factories.person_address import PersonAddressFactory
from internship.forms.internship_person_address_form import InternshipPersonAddressForm
from reference.tests.factories.country import CountryFactory


class TestInternshipPersonAddressForm(TestCase):
    def test_valid_form(self):
        data = {
            "location": "test",
            "city": "test",
            "postal_code": "1000",
            "country": CountryFactory().pk,
        }
        person_address_form = InternshipPersonAddressForm(data)
        self.assertTrue(person_address_form.is_valid())

    def test_invalid_country(self):
        data = {
            "country": "no_country",
        }
        form = InternshipPersonAddressForm(data)
        self.assertFalse(form.is_valid())
        self.assertTrue('country' in form.errors.keys())

    def test_fields_enabled_for_instance_with_internship_source(self):
        person_address = PersonAddressFactory(person__source=INTERNSHIP)
        form = InternshipPersonAddressForm(instance=person_address)
        for field in form.fields.values():
            self.assertFalse(field.disabled)

    def test_fields_disabled_for_other_instance_sources(self):
        person_address = PersonAddressFactory(person__source=BASE)
        form = InternshipPersonAddressForm(instance=person_address)
        for field in form.fields.values():
            self.assertTrue(field.disabled)
