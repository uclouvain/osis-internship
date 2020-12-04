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

from django.test import TestCase
from django.utils import timezone

from internship.forms.internship_person_form import InternshipPersonForm


class TestInternshipPersonForm(TestCase):
    def test_valid_form(self):
        data = {
            "first_name": "test",
            "last_name": "test",
            "gender": "M",
            "email": "test@test.com",
            'birth_date': "1980-01-01",
        }
        person_form = InternshipPersonForm(data)
        self.assertTrue(person_form.is_valid())

    def test_invalid_birth_date(self):
        data = {
            "last_name": "test",
            'birth_date': timezone.now().date() + timedelta(days=5),
        }
        form = InternshipPersonForm(data)
        self.assertFalse(form.is_valid())
