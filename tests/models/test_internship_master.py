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
from django.test.testcases import TestCase

from internship.models import internship_master
from internship.tests.factories.master import MasterFactory


class TestInternshipMaster(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.master = MasterFactory()

    def test_get_by_id(self):
        persisted_master = internship_master.get_by_id(self.master.id)
        self.assertEqual(self.master.id, persisted_master.id)

        nonexistent_master = internship_master.get_by_id(0)
        self.assertIsNone(nonexistent_master)

    def test_civility_acronym(self):
        self.assertTrue("." in self.master.civility_acronym())
