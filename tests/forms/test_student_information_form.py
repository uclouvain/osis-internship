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

from base.tests.factories.person import PersonFactory
from internship.forms import form_student_information
from internship.tests.factories.cohort import CohortFactory
from reference.tests.factories.country import CountryFactory


class TestFormStudentInformation(TestCase):
    def test_valid_form(self):
        country = CountryFactory()
        cohort = CohortFactory()
        person = PersonFactory()
        data = {
            "email": "test@test.com",
            "phone_mobile": "046486313",
            "location": "location",
            "postal_code": "postal",
            "city": "city",
            "country": country,
            "contest": "GENERALIST",
            "person": person.id,
            'cohort': cohort.id,
        }
        form = form_student_information.StudentInformationForm(data)
        self.assertTrue(form.is_valid())

