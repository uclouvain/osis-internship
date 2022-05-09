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
from types import SimpleNamespace

from django.test import TestCase

from internship.templatetags.student import is_searched_reference
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory


class TestStudentTemplateTags(TestCase):
    def test_is_searched_reference(self):
        organization = OrganizationFactory(reference='01')
        specialty = SpecialtyFactory(acronym='ACR')
        request = SimpleNamespace(GET={'organization': organization.pk, 'specialty': specialty.pk})

        self.assertTrue(is_searched_reference('ACR01', request))

    def test_is_not_searched_reference(self):
        organization = OrganizationFactory(reference='01')
        specialty = SpecialtyFactory(acronym='ACR')
        request = SimpleNamespace(GET={'organization': organization.pk, 'specialty': specialty.pk})

        self.assertFalse(is_searched_reference('ACR02', request))

    def test_is_searched_reference_without_specialty(self):
        organization = OrganizationFactory(reference='01')
        request = SimpleNamespace(GET={'organization': organization.pk})

        self.assertTrue(is_searched_reference('XX01', request))

    def test_is_searched_reference_without_organization(self):
        specialty = SpecialtyFactory(acronym='ACR')
        request = SimpleNamespace(GET={'specialty': specialty.pk})

        self.assertTrue(is_searched_reference('ACR05', request))
