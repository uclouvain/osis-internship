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
from freezegun import freeze_time

from internship.models import master_allocation
from internship.models.internship_master import InternshipMaster
from internship.models.master_allocation import MasterAllocation
from internship.tests.factories.master import MasterFactory
from internship.tests.factories.master_allocation import MasterAllocationFactory
from internship.tests.factories.organization import OrganizationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.speciality import SpecialtyFactory


class TestInternshipMaster(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.master = MasterFactory()

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
        allocated_masters = MasterAllocation.objects.values("pk").distinct()
        unallocated_masters = InternshipMaster.objects.exclude(id__in=(list([a['pk'] for a in allocated_masters]))) \
            .order_by('person__last_name', 'person__first_name')
        self.assertEqual(1, unallocated_masters.count())

    def test_clean_allocations(self):
        allocation = MasterAllocationFactory(master=self.master)
        cohort = allocation.specialty.cohort
        master_allocation.clean_allocations(cohort, self.master, postpone=False)
        allocations = master_allocation.find_by_master(cohort, self.master)
        self.assertEqual(0, allocations.count())

    @freeze_time("2023-10-09")
    def test_clean_allocations_with_postponement(self):
        allocation = MasterAllocationFactory(master=self.master)
        cohort1 = allocation.organization.cohort
        PeriodFactory(name='P1cohort1', date_start='2023-10-10', date_end='2023-10-20', cohort=cohort1)

        allocation = MasterAllocationFactory(master=self.master)
        cohort2 = allocation.organization.cohort
        PeriodFactory(name='P1cohort2', date_start='2023-10-10', date_end='2023-10-20', cohort=cohort2)

        master_allocation.clean_allocations(cohort1, self.master, postpone=True)

        allocations = MasterAllocation.objects.filter(master=self.master)
        self.assertEqual(0, allocations.count())

    @freeze_time("2023-10-09")
    def test_clean_allocations_without_postponement(self):
        allocation = MasterAllocationFactory(master=self.master)
        cohort1 = allocation.organization.cohort
        PeriodFactory(name='P1cohort1', date_start='2023-10-10', date_end='2023-10-20', cohort=cohort1)

        allocation = MasterAllocationFactory(master=self.master)
        cohort2 = allocation.organization.cohort
        PeriodFactory(name='P1cohort2', date_start='2023-10-10', date_end='2023-10-20', cohort=cohort2)

        master_allocation.clean_allocations(cohort1, self.master, postpone=False)

        allocations = MasterAllocation.objects.filter(master=self.master)
        self.assertEqual(1, allocations.count())
