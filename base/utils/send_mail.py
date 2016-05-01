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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

"""
Utility files for mail sending
"""
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils.translation import ugettext as _

from backoffice.settings import DEFAULT_FROM_EMAIL, LOGO_OSIS_URL, LOGO_EMAIL_SIGNATURE_URL
from base.models import message_template


def send_mail_after_scores_submission(persons, learning_unit_name, submitted_enrollments, all_encoded):
    """
    Send an email to all the teachers after the scores submission for a learning unit
    :param persons: The list of the teachers of the leaning unit
    :param learning_unit_name: The name of the learning unit for which scores were submitted
    :param submitted_enrollments : The list of newly sibmitted enrollments
    :param all_encoded : Tell if all the scores are encoded and submitted
    """

    txt_message_template = message_template.find_by_reference('assessments_scores_submission_txt_fr')
    html_message_template = message_template.find_by_reference('assessments_scores_submission_html_fr')
    subject = str(html_message_template.subject).format(learning_unit_name=learning_unit_name)

    submitted_enrollments_data = [
        {
            'offer_year_acronym':   enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
            'session':              enrollment.session_exam.number_session,
            'std_registration_id':  enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
            'std_last_name':        enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
            'std_first_name':       enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
            'final_score':          enrollment.score_final,
            'justification_final':  enrollment.justification_final,
        } for enrollment in submitted_enrollments]

    data = {
        'learning_unit_name':       learning_unit_name,
        'submitted_enrollments':    submitted_enrollments_data,
        'all_encoded':              all_encoded,
        'logo_mail_signature_url':  LOGO_OSIS_URL,
        'logo_osis_url':            LOGO_EMAIL_SIGNATURE_URL,
    }

    html_message = Template(html_message_template.template).render(Context(data))
    txt_changes = '\n\n'.join([
        " - ".join([
            str(enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym),
            str(enrollment.session_exam.number_session),
            str(enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id),
            str(enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name),
            str(enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name),
            str(enrollment.score_final),
            str(enrollment.justification_final)
        ])
        for enrollment in submitted_enrollments])
    if all_encoded:
        txt_encoding_status = _('encoding_status_ended')
    else:
        txt_encoding_status = _('encoding_status_notended')
    txt_message = txt_message_template.template.format(changes=txt_changes, encoding_status=txt_encoding_status, **data)

    send_mail(subject=subject, message=txt_message, recipient_list=[person.email for person in persons if person.email],
              html_message=html_message, from_email=DEFAULT_FROM_EMAIL)


def send_mail_after_academic_calendar_changes(academic_calendar, offer_year_calendar, programm_managers):
    """
    Send an email to all the programme manager after changes has been made on a offer_year_calendar with customized
    = True
    :param academic_calendar:
    :param offer_year_calendar:
    :param programm_managers:
    """

    txt_message_template = message_template.find_by_reference('academic_calendar_changes_txt_fr')
    html_message_template = message_template.find_by_reference('academic_calendar_changes_html_fr')
    subject = str(html_message_template.subject).format(offer_year=str(offer_year_calendar.offer_year.acronym),
                                                        academic_calendar=str(academic_calendar))

    data = {
        'offer_year_title':         offer_year_calendar.offer_year.title,
        'offer_year_acronym':       offer_year_calendar.offer_year.acronym,
        'academic_calendar':        str(academic_calendar),
        'logo_mail_signature_url':  LOGO_OSIS_URL,
        'logo_osis_url':            LOGO_EMAIL_SIGNATURE_URL,
    }

    html_message = Template(html_message_template.template).render(Context(data))
    message = txt_message_template.template.format(**data)
    recipient_list = [manager.person.email for manager in programm_managers if manager.person.email]
    send_mail(subject=subject,
              message=message,
              recipient_list=recipient_list,
              html_message=html_message,
              from_email=DEFAULT_FROM_EMAIL)

