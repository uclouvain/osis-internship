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
from html import unescape

from django.core.mail import send_mail
from django.template import Template, Context
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.html import strip_tags
from django.utils.translation import ugettext as _

from backoffice import settings
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

    txt_message_templates = {template.language: template for template in
                             message_template.find_by_reference('assessments_scores_submission_txt')}
    html_message_templates = {template.language: template for template in
                              message_template.find_by_reference('assessments_scores_submission_html')}

    submitted_enrollments_data = [
        (
            enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
            enrollment.session_exam.number_session,
            enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
            enrollment.score_final,
            enrollment.justification_final,
        ) for enrollment in submitted_enrollments]

    data = {
        'learning_unit_name': learning_unit_name,
        'signature': render_to_string('email/html_email_signature.html', {
            'logo_mail_signature_url': LOGO_OSIS_URL,
            'logo_osis_url': LOGO_EMAIL_SIGNATURE_URL,
        })
    }

    dest_by_lang = map_persons_emails_by_languages([person for person in persons if person.email])
    for lang_code, emails in dest_by_lang.items():
        if emails:
            if lang_code in html_message_templates:
                html_message_template = html_message_templates[lang_code]
            else:
                html_message_template = html_message_templates[settings.LANGUAGE_CODE]
            if txt_message_templates[lang_code]:
                txt_message_template = txt_message_templates[lang_code]
            else:
                txt_message_template = txt_message_templates[settings.LANGUAGE_CODE]
            with translation.override(lang_code):
                submitted_enrollment_header = (
                    _('acronym'),
                    _('session'),
                    _('registration_number'),
                    _('lastname'),
                    _('firstname'),
                    _('score'),
                    _('documentation')
                )
                submitted_enrollments_table_html = render_table_template_as_string(
                    submitted_enrollment_header,
                    submitted_enrollments_data,
                    True
                )
                data['encoding_status'] = _('encoding_status_ended') if all_encoded else _('encoding_status_notended')
                data['submitted_enrollments'] = submitted_enrollments_table_html
                html_message = Template(html_message_template.template).render(Context(data))
                subject = html_message_template.subject.format(learning_unit_name=learning_unit_name)
                submitted_enrollments_table_txt = render_table_template_as_string(
                    submitted_enrollment_header,
                    submitted_enrollments_data,
                    False
                )
                data['submitted_enrollments'] = submitted_enrollments_table_txt
                txt_message = Template(txt_message_template.template).render(Context(data))
                send_mail(subject=unescape(strip_tags(subject)),
                          message=unescape(strip_tags(txt_message)),
                          recipient_list=[email for email in emails if email],
                          html_message=html_message, from_email=DEFAULT_FROM_EMAIL)


def send_mail_after_academic_calendar_changes(academic_calendar, offer_year_calendar, programm_managers):
    """
    Send an email to all the programme manager after changes has been made on a offer_year_calendar with customized
    = True
    :param academic_calendar:
    :param offer_year_calendar:
    :param programm_managers:
    """
    txt_message_templates = {template.language: template for template in
                             message_template.find_by_reference('academic_calendar_changes_txt')}
    html_message_templates = {template.language: template for template in
                              message_template.find_by_reference('academic_calendar_changes_html')}

    data = {
        'offer_year_title':         offer_year_calendar.offer_year.title,
        'offer_year_acronym':       offer_year_calendar.offer_year.acronym,
        'academic_calendar':        str(academic_calendar),
        'signature':                render_to_string('email/html_email_signature.html', {
            'logo_mail_signature_url': LOGO_OSIS_URL,
            'logo_osis_url': LOGO_EMAIL_SIGNATURE_URL,
            })
    }

    dest_by_lang = map_persons_emails_by_languages([manager.person for manager in programm_managers
                                                    if manager.person.email])
    for lang_code, emails in dest_by_lang.items():
        if lang_code in html_message_templates:
            html_message_template = html_message_templates[lang_code]
        else:
            html_message_template = html_message_templates[settings.LANGUAGE_CODE]
        if lang_code in txt_message_templates:
            txt_message_template = txt_message_templates[lang_code]
        else:
            txt_message_template = txt_message_templates[settings.LANGUAGE_CODE]
        with translation.override(lang_code):
            html_message = Template(html_message_template.template).render(Context(data))
            message = Template(txt_message_template.template).render(Context(data))
            subject = str(html_message_template.subject).format(offer_year=str(offer_year_calendar.offer_year.acronym),
                                                                academic_calendar=str(academic_calendar))
            send_mail(subject=unescape(strip_tags(subject)),
                      message=unescape(strip_tags(message)),
                      recipient_list=emails,
                      html_message=html_message,
                      from_email=DEFAULT_FROM_EMAIL)


def render_table_template_as_string(table_headers, table_rows, html_format):
    """
     Render the table template as a string.
     If htmlformat is True , render the html table template , else the txt table template
     Used to create dynamically a table of data to insert into email template.
     :param table_headers: The header of the table as a list of Strings
     :param table_rows: The content of each row as a list of item list
     :param html_format True if you want the html template , False if you want the txt template
    """
    if html_format:
        template = 'email/html_email_table_template.html'
    else:
        template = 'email/txt_email_table_template.html'
    data = {
        'table_headers': table_headers,
        'table_rows': table_rows
    }
    return render_to_string(template, data)


def map_persons_emails_by_languages(persons):
    """
    Convert a list of persons into a dictionnary langage_code: list_of_emails ,
    according to the language of the person.
    :param persons the list of persons we want to map
    """
    lang_dict = {lang[0]: [] for lang in settings.LANGUAGES}
    for person in persons:
        if person.language in lang_dict.keys():
            lang_dict[person.language].append(person.email)
        else:
            lang_dict[settings.LANGUAGE_CODE].append(person)
    return lang_dict
