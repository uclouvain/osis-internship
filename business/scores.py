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
from base.models.student import Student
from internship.models.internship_student_affectation_stat import InternshipStudentAffectationStat
from internship.models.internship_student_information import InternshipStudentInformation
from internship.models.period import Period
from osis_common.messaging import message_config
from osis_common.messaging.send_message import send_messages


class InternshipScoreRules:
    NORMAL_GRADES = ['C', 'D', 'E']
    EXCEPT_APDS = [8, 14]
    EXCEPT_GRADES = NORMAL_GRADES + ['B']

    @classmethod
    def get_valid_grades(self, index):
        return self.EXCEPT_GRADES if index in self.get_except_apds_indices() else self.NORMAL_GRADES

    @classmethod
    def get_except_apds_indices(self):
        return [x - 1 for x in self.EXCEPT_APDS]

    @classmethod
    def is_score_valid(self, index, score):
        return score in self.get_valid_grades(index)

    @classmethod
    def student_has_fulfilled_requirements(self, student):
        if not student.scores:
            return False
        for period, scores in student.scores:
            for index, score in enumerate(scores):
                if score and not self.is_score_valid(index, score):
                    return False
        return True


def send_score_encoding_reminder(data):
    student_info = InternshipStudentInformation.objects.get(
        person__id=data['person_id'],
        cohort__id=data['cohort_id']
    )
    student = Student.objects.get(person__id=data['person_id'])
    periods = Period.objects.filter(pk__in=data['periods']).order_by('start_date')
    affectations = InternshipStudentAffectationStat.objects.filter(
        student=student, period__in=periods
    )
    message_content = message_config.create_message_content(
        html_template_ref='internship_score_encoding_reminder_email_html',
        txt_template_ref='internship_score_encoding_reminder_email_txt',
        tables=[],
        receivers=[message_config.create_receiver(
            student_info.person_id,
            student_info.email,
            None
        )],
        template_base_data={
            'student': student,
            'affectations': affectations
        },
        subject_data={}
    )
    send_messages(message_content=message_content)
