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

from django.conf import settings
from django.test import TestCase
from django.utils.datetime_safe import date

from base.tests.factories.student import StudentFactory
from internship.models.enums.user_account_status import UserAccountStatus
from internship.models.internship_score import APD_NUMBER, InternshipScore
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship_student_information import InternshipStudentInformationFactory
from internship.tests.factories.master_allocation import MasterAllocationFactory
from internship.tests.factories.period import PeriodFactory
from internship.tests.factories.student_affectation_stat import StudentAffectationStatFactory
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


class InternshipPeriodEncodingReminderTest(TestCase):

    def setUp(self) -> None:
        self.cohort = CohortFactory()
        self.period = PeriodFactory(cohort=self.cohort, date_end=date.today())
        self.active_master_allocation = MasterAllocationFactory(
            specialty__cohort=self.cohort, organization__cohort=self.cohort,
            master__user_account_status=UserAccountStatus.ACTIVE.value
        )
        self.student_affectation = StudentAffectationStatFactory(
            speciality=self.active_master_allocation.specialty,
            organization=self.active_master_allocation.organization,
            period=self.period
        )
        self.inactive_master_allocation = MasterAllocationFactory(
            specialty__cohort=self.cohort, organization__cohort=self.cohort,
            master__user_account_status=UserAccountStatus.INACTIVE.value
        )

    @mock.patch('internship.utils.mails.mails_management.send_messages')
    def test_send_internship_period_encoding_reminder_only_to_active_master_with_affectations(self, mock_send_messages):
        mails_management.send_internship_period_encoding_reminder(self.period)
        _, args = mock_send_messages.call_args
        self.assertTrue(mock_send_messages.called)
        self.assertEqual(args['message_content']['template_base_data'], {
            'link': settings.INTERNSHIP_SCORE_ENCODING_URL,
            'period': self.period.name
        })
        self.assertEqual(args['message_content']['receivers'][0], {
            **args['message_content']['receivers'][0],
            'receiver_email': self.active_master_allocation.master.person.email,
            'receiver_person_id': self.active_master_allocation.master.person_id,
        })
        self.period.refresh_from_db()
        self.assertTrue(self.period.reminder_mail_sent)


class InternshipPeriodEncodingRecapTest(TestCase):

    def setUp(self) -> None:
        self.cohort = CohortFactory()
        self.period = PeriodFactory(cohort=self.cohort)
        self.allocation = MasterAllocationFactory(
            specialty__cohort=self.cohort, organization__cohort=self.cohort,
            master__user_account_status=UserAccountStatus.ACTIVE.value
        )
        self.affectation = StudentAffectationStatFactory(
            speciality=self.allocation.specialty,
            organization=self.allocation.organization,
            period=self.period
        )
        self.inactive_master_allocation = MasterAllocationFactory(
            specialty=self.allocation.specialty, organization=self.allocation.organization,
            master__user_account_status=UserAccountStatus.INACTIVE.value
        )

    @mock.patch('internship.utils.mails.mails_management.send_messages')
    def test_send_internship_period_encoding_recap_only_to_active_master_create_empty_score(self, mock_send_messages):
        self.assertFalse(InternshipScore.objects.exists())
        mails_management.send_internship_period_encoding_recap(self.period)
        _, args = mock_send_messages.call_args
        self.assertTrue(mock_send_messages.called)
        data = {
            'apds': ['{}'.format(index) for index in range(1, APD_NUMBER + 1)],
            'allocation': self.allocation,
            'period': self.period.name,
            'link': settings.INTERNSHIP_SCORE_ENCODING_URL,
        }
        for key in data.keys():
            self.assertEqual(args['message_content']['template_base_data'][key], data[key])
        self.assertTrue(InternshipScore.objects.exists())
        self.assertEqual(args['message_content']['receivers'][0], {
            **args['message_content']['receivers'][0],
            'receiver_email': self.allocation.master.person.email,
            'receiver_person_id': self.allocation.master.person_id,
        })
