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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.contrib.auth.models import User, Permission
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import TestCase, RequestFactory

from internship.views.common import get_object_list, PAGINATOR_SIZE_LIST

OBJECTS_LIST_SIZE = 50
TEST_PAGINATOR_SIZE = 25


class CommonTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('demo', 'demo@demo.org', 'passtest')
        permission = Permission.objects.get(codename='is_internship_manager')
        cls.user.user_permissions.add(permission)

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_object_list_with_default_paginator_size(self):
        objects = [{} for _ in range(0, OBJECTS_LIST_SIZE)]
        request = RequestFactory().get('/')
        SessionMiddleware().process_request(request)
        self.assertEqual(len(get_object_list(request, objects)), PAGINATOR_SIZE_LIST[0])

    def test_get_object_list_with_paginator_size_query_param(self):
        objects = [{} for _ in range(0, OBJECTS_LIST_SIZE)]
        request = RequestFactory().get('/?paginator_size={}'.format(TEST_PAGINATOR_SIZE))
        SessionMiddleware().process_request(request)
        self.assertEqual(len(get_object_list(request, objects)), TEST_PAGINATOR_SIZE)
        self.assertEqual(request.session['paginator_size'], {request.path: str(TEST_PAGINATOR_SIZE)})
