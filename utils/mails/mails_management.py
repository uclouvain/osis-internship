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
from internship.models.internship_student_information import InternshipStudentInformation
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
            'periods': data['periods']
        },
        subject_data={}
    )
    send_messages(message_content=message_content, connected_user=connected_user)
