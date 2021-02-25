##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2020 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.conf import settings

from internship.models.enums.user_account_status import UserAccountStatus
from internship.models.internship_score import InternshipScore, APD_NUMBER
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.master_allocation import MasterAllocation
from osis_common.messaging import message_config
from osis_common.messaging.send_message import send_messages


def send_score_encoding_recap(data, connected_user):
    student_info = InternshipStudentInformation.objects.get(
        person__id=data['person_id'],
        cohort__id=data['cohort_id']
    )
    message_content = message_config.create_message_content(
        html_template_ref='internship_score_encoding_recap_email_html',
        txt_template_ref='internship_score_encoding_recap_email_txt',
        tables=[],
        receivers=[message_config.create_receiver(
            student_info.person_id,
            student_info.email,
            None
        )],
        template_base_data={
            'today': data['today'],
            'periods': data['periods'],
            'ordered_periods': data['ordered_periods']
        },
        subject_data={}
    )
    send_messages(message_content=message_content, connected_user=connected_user)


def send_internship_period_encoding_reminder(period):
    organizations, specialties = _get_effective_internships_data(period)
    active_user_allocations = _get_active_user_allocations(organizations, specialties)
    deduped_active_masters = _get_deduped_active_masters(active_user_allocations)

    message_content = message_config.create_message_content(
        html_template_ref='internship_end_period_reminder_html',
        txt_template_ref='internship_end_period_reminder_txt',
        tables=[],
        receivers=[message_config.create_receiver(
            master['person_id'],
            master['email'],
            None
        ) for master in deduped_active_masters],
        template_base_data={
            'period': period.name,
            'link': settings.INTERNSHIP_SCORE_ENCODING_URL
        },
        subject_data={'period': period.name}
    )
    send_messages(message_content=message_content)
    period.reminder_mail_sent = True
    period.save()


def send_internship_score_encoding_recaps(period):
    organizations, specialties = _get_effective_internships_data(period)
    active_user_allocations = _get_active_user_allocations(organizations, specialties)
    students_affectations = InternshipStudentAffectationStat.objects.filter(period=period)

    for allocation in active_user_allocations:
        scores = _get_allocation_scores(allocation, period, students_affectations)
        message_content = message_config.create_message_content(
            html_template_ref='internship_end_period_recap_html',
            txt_template_ref='internship_end_period_recap_txt',
            tables=[],
            receivers=[message_config.create_receiver(
                allocation.master.person_id,
                allocation.master.person.email,
                None
            )],
            template_base_data={
                'apds': ['{}'.format(index) for index in range(1, APD_NUMBER+1)],
                'allocation': allocation,
                'scores': scores,
                'period': period.name,
                'link': settings.INTERNSHIP_SCORE_ENCODING_URL
            },
            subject_data={'period': period.name}
        )
        send_messages(message_content=message_content)


def _get_active_user_allocations(organizations, specialties):
    return MasterAllocation.objects.filter(
        specialty_id__in=specialties,
        organization_id__in=organizations,
        master__user_account_status=UserAccountStatus.ACTIVE.value
    ).select_related('master__person', 'organization', 'specialty')


def _get_effective_internships_data(period):
    effective_internships = InternshipStudentAffectationStat.objects.filter(
        period=period
    ).values_list('speciality_id', 'organization_id', named=True)
    specialties, organizations = zip(*[(i.speciality_id, i.organization_id) for i in effective_internships])
    return organizations, specialties


def _get_deduped_active_masters(active_user_allocations):
    active_masters = [{
        'person_id': allocation.master.person_id,
        'email': allocation.master.person.email
    } for allocation in active_user_allocations]
    deduped_active_masters = list({master['email']: master for master in active_masters}.values())
    return deduped_active_masters


def _get_allocation_scores(allocation, period, students_affectations):
    students = students_affectations.filter(
        organization=allocation.organization,
        speciality=allocation.specialty
    ).values_list('student_id', flat=True)
    _fill_with_empty_scores(period, students)
    scores = InternshipScore.objects.filter(
        period=period, student_id__in=students
    ).select_related('student__person')
    return scores


def _fill_with_empty_scores(period, students):
    InternshipScore.objects.bulk_create(
        [InternshipScore(student_id=student, period=period, cohort=period.cohort) for student in students],
        ignore_conflicts=True,
        batch_size=1000
    )
