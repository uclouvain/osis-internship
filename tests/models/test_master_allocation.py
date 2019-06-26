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

from internship.models import master_allocation
from internship.tests.factories.master import MasterFactory
from internship.tests.factories.master_allocation import MasterAllocationFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.speciality import SpecialtyFactory


class TestInternshipMaster(TestCase):
    def setUp(self):
        self.master = MasterFactory()

    def test_save_duplicated(self):
        organization = OrganizationFactory()
        specialty = SpecialtyFactory()

        MasterAllocationFactory(organization=organization, specialty=specialty, master=self.master)
        MasterAllocationFactory(organization=organization, specialty=specialty, master=self.master)

        allocations = master_allocation.find_by_master(specialty.cohort, self.master)
        self.assertEqual(1, allocations.count())

    def test_find_by_master(self):
        allocation = MasterAllocationFactory(master=self.master)
        allocations = master_allocation.find_by_master(allocation.specialty.cohort, self.master)
        self.assertEqual(self.master, allocations[0].master)

    def test_find_unallocated_masters(self):
        unallocated_masters = master_allocation.find_unallocated_masters()
        self.assertEqual(1, unallocated_masters.count())

    def test_clean_allocations(self):
        allocation = MasterAllocationFactory(master=self.master)
        cohort = allocation.specialty.cohort
        master_allocation.clean_allocations(cohort, self.master)
        allocations = master_allocation.find_by_master(cohort, self.master)
        self.assertEqual(0, allocations.count())
