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
import datetime
from unittest import mock

from django.test import TestCase

from base.tests.factories.student import StudentFactory
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.period import PeriodFactory
from internship.utils.mails import mails_management


class InternshipScoreRecapTest(TestCase):
    def setUp(self) -> None:
        self.cohort = CohortFactory()
        self.student_info = InternshipStudentInformationFactory(cohort=self.cohort)
        self.student = StudentFactory(person=self.student_info.person)
        self.period = PeriodFactory(cohort=self.cohort)

    @mock.patch('internship.utils.mails.mails_management.send_score_encoding_recap')
    def test_send_recap(self, mock_send_messages):
        data = {
            'today': datetime.date.today(),
            'person_id': self.student_info.person.pk,
            'cohort_id': self.cohort.pk,
            'periods': {self.student_info.person: {self.period.name: "OK"}}
        }

        mails_management.send_score_encoding_recap(data, None)
        self.assertTrue(mock_send_messages.called)
