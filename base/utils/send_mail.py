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
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from backoffice.settings import DEFAULT_FROM_EMAIL, LOGO_OSIS_URL, LOGO_EMAIL_SIGNATURE_URL

base_data = {
    'logo_mail_signature_url': LOGO_OSIS_URL,
    'logo_osis_url': LOGO_EMAIL_SIGNATURE_URL,
}


def send_mail_after_scores_submission(persons, learning_unit_name):
    """
    Send an email to all the teachers after the scores submission for a learning unit
    :param persons: The list of the teachers of the leaning unit
    :param learning_unit_name: The name of the learning unit for wihch scores were submitted
    """

    subject = _('submission_of_scores_for').format(learning_unit_name)
    html_message = render_to_string('emails/scores_submission.txt', {'format_args': learning_unit_name})
    message = render_to_string('emails/scores_submission.html',
                               dict(list(base_data.items()) + list({'format_args': learning_unit_name}.items())))
    send_mail(subject=subject, message=message, recipient_list=[person.email for person in persons if person.email],
              html_message=html_message, from_email=DEFAULT_FROM_EMAIL)


def send_mail_after_academic_calendar_changes(academic_calendar, offer_year_calendar, programm_managers):
    """
    Send an email to all the programme manager after changes has been made on a offer_year_calendar with customized
    = True
    :param academic_calendar:
    :param offer_year_calendar:
    :param programm_managers:
    """
    subject = _('mail_academic_calendar_change_subject').format(str(offer_year_calendar.offer_year),
                                                                str(academic_calendar))
    format_args = '|'.join([offer_year_calendar.offer_year.title, offer_year_calendar.offer_year.acronym,
                            str(academic_calendar)])
    html_message = render_to_string('emails/academic_calendar_changes.html',
                                    dict(list(base_data.items()) + list({'format_args': format_args}.items())))
    message = render_to_string('emails/academic_calendar_changes.txt', {'format_args': format_args})

    send_mail(subject=subject,
              message=message,
              recipient_list=[manager.person.email for manager in list(programm_managers) if manager.person.email],
              html_message=html_message,
              from_email=DEFAULT_FROM_EMAIL)

