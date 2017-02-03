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
import datetime
from django.test import TestCase
from base.models import synchronization
from django.core.exceptions import ObjectDoesNotExist
import datetime


def create_synchronization(date=datetime.datetime.now()):
    sync = synchronization.Synchronization(date=date)
    sync.save()
    return sync


class MultipleSynchronizationTest(TestCase):

    def setUp(self):
        self.current_year = datetime.datetime.now().year
        create_synchronization(date=datetime.datetime(self.current_year, 10, 28, 20, 00, 59, 99999))
        self.latest_sync_id = create_synchronization(date=datetime.datetime(self.current_year, 10, 28, 20, 1, 0, 0)).id
        create_synchronization(date=datetime.datetime(self.current_year, 10, 27, 23, 59, 59, 99999))

    def test_find_last_synchronization_date(self):
        sync = synchronization.Synchronization.objects.get(pk=self.latest_sync_id)
        self.assertEquals(sync.date, synchronization.find_last_synchronization_date())


class InexistingSynchronizationTest(TestCase):

    def test_find_last_syncrhonization_date(self):
        self.assertRaises(ObjectDoesNotExist, synchronization.find_last_synchronization_date())
