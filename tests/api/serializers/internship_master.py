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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import TestCase, override_settings
from rest_framework.exceptions import ValidationError

from base.tests.factories.person import PersonFactory
from base.tests.factories.user import UserFactory
from internship.api.serializers.internship_master import InternshipMasterSerializer


class InternshipMasterSerializerTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client.force_login(self.user)

    @override_settings(INTERNAL_EMAIL_SUBDOMAINS=['subdomain'])
    def test_email_with_stripped_subdomain_already_exists(self):
        existing_person = PersonFactory(email='test@osis.org')
        serializer = InternshipMasterSerializer(data={'person': {'email': "test@subdomain.osis.org"}})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
