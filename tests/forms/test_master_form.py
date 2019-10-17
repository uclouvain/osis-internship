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
from datetime import timedelta

from django.test import TestCase, RequestFactory
from django.utils import timezone

from internship.forms import master
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory
from internship.views.master import _validate_allocations
from reference.models.country import Country


class TestMasterForm(TestCase):

    def test_valid_form(self):
        belgium = Country.find_by_uuid("ae40df86-04e9-4e9b-8dca-0c1e26b1476d")
        data = {
            "first_name": "test",
            "last_name": "test",
            "civility": "DOCTOR",
            "gender": "M",
            "email": "test@test.com",
            "email_private": "test@test.com",
            "phone_mobile": "00000000",
            "location": "location",
            "postal_code": "1348",
            "city": "city",
            "country": belgium,
            'birth_date': "1980-01-01",
            'start_activities': "2000-01-01",
        }
        form = master.MasterForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_birth_date(self):
        data = {
            "last_name": "test",
            'birth_date': timezone.now().date() + timedelta(days=5),
        }
        form = master.MasterForm(data)
        self.assertFalse(form.is_valid())

    def test_invalid_allocation(self):
        requetFactory = RequestFactory()
        request = requetFactory.post("/masters/save/",data={
            "specialty": [''],
            "hospital": ['']
        })
        self.assertFalse(_validate_allocations(request))

    def test_valid_allocation_one_specialty(self):
        requetFactory = RequestFactory()
        request = requetFactory.post("/masters/save/",data={
            "specialty": [''],
            "hospital": [OrganizationFactory()]
        })
        self.assertTrue(_validate_allocations(request))

    def test_valid_allocation_one_hospital(self):
        requetFactory = RequestFactory()
        request = requetFactory.post("/masters/save/",data={
            "specialty": [SpecialtyFactory()],
            "hospital": ['']
        })
        self.assertTrue(_validate_allocations(request))

    def test_valid_allocation_both(self):
        requetFactory = RequestFactory()
        request = requetFactory.post("/masters/save/",data={
            "specialty": [SpecialtyFactory()],
            "hospital": [OrganizationFactory()]
        })
        self.assertTrue(_validate_allocations(request))
