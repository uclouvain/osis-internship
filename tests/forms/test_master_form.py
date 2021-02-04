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

from internship.forms import master
from internship.models.enums.role import Role
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.views.master import _validate_allocations
from reference.models.country import Country


class TestMasterForm(TestCase):
    def test_valid_form(self):
        belgium = Country.find_by_uuid("ae40df86-04e9-4e9b-8dca-0c1e26b1476d")
        data = {
            "email_private": "test@test.com",
            "phone_mobile": "00000000",
            "location": "location",
            "postal_code": "1348",
            "city": "city",
            "country": belgium,
            'start_activities': "2000-01-01",
            "role": Role.MASTER.value,
        }
        master_form = master.MasterForm(data)
        self.assertTrue(master_form.is_valid())

    def test_invalid_allocation(self):
        request = self.client.post("/masters/save/",data={
            "specialty": [''],
            "hospital": ['']
        }).wsgi_request
        self.assertFalse(_validate_allocations(request))

    def test_valid_allocation_one_specialty(self):
        request = self.client.post("/masters/save/",data={
            "specialty": [''],
            "hospital": [OrganizationFactory()]
        }).wsgi_request
        self.assertTrue(_validate_allocations(request))

    def test_valid_allocation_one_hospital(self):
        request = self.client.post("/masters/save/",data={
            "specialty": [SpecialtyFactory()],
            "hospital": ['']
        }).wsgi_request
        self.assertTrue(_validate_allocations(request))

    def test_valid_allocation_both(self):
        request = self.client.post("/masters/save/",data={
            "specialty": [SpecialtyFactory()],
            "hospital": [OrganizationFactory()]
        }).wsgi_request
        self.assertTrue(_validate_allocations(request))
