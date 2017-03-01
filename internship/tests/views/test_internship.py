##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from base.tests.models import test_person


class TestUrlAccess(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("username", "test@test.com", "passtest")
        self.user.first_name = "first_name"
        self.user.last_name = "last_name"
        self.user.save()
        add_permission(self.user, "is_internship_manager")
        self.person = test_person.create_person_with_user(self.user)
        self.c = Client()

    def test_can_access_internship_modfication_student(self):
        url = reverse("internships_modification_student")

        response = self.c.get(url)
        self.assertEqual(response.status_code, 302)

        self.c.force_login(self.user)
        response = self.c.get(url)
        self.assertEqual(response.status_code, 200)


def add_permission(user, codename):
    perm = get_permission(codename)
    user.user_permissions.add(perm)


def get_permission(codename):
    return Permission.objects.get(codename=codename)