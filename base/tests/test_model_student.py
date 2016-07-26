##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

# This class tests the portal_migration functions.


from django.test import TestCase
from base.models import student, person
from django.contrib.auth.models import User
from django.core import serializers
import backoffice.tests.data_for_tests as data_for_tests


class PortalMigrationTest(TestCase):
    def setUp(self):
        self.list_students = data_for_tests.create_students()

    def testFindAllForSync(self):
        #TODO implement test
        list_actual = student.find_all_for_sync()
        print(list_actual)
        self.assertEqual(1, 1)
