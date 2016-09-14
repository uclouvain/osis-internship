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

from django.utils.translation import ugettext as _

from osis_common.models import message_history as message_history_mdl
from osis_common.messaging import message_config, send_message as message_service
from base.models import person as person_mdl


def send_mail_after_scores_submission(persons, learning_unit_name, submitted_enrollments, all_encoded):
    """
    Send an email to all the teachers after the scores submission for a learning unit
    :param persons: The list of the teachers of the leaning unit
    :param learning_unit_name: The name of the learning unit for which scores were submitted
    :param submitted_enrollments : The list of newly sibmitted enrollments
    :param all_encoded : Tell if all the scores are encoded and submitted
    :return An error message if the template is not in the database
    """

    html_template_ref = 'assessments_scores_submission_html'
    txt_template_ref = 'assessments_scores_submission_txt'
    receivers = [message_config.create_receiver(person.id, person.email, person.language) for person in persons]
    suject_data = {'learning_unit_name': learning_unit_name}
    template_base_data = {'learning_unit_name': learning_unit_name,
                          'encoding_status':    _('encoding_status_ended') if all_encoded
                          else _('encoding_status_notended')
                          }
    header_txt = ['acronym', 'sessionn', 'registration_number', 'lastname', 'firstname', 'score', 'documentation']
    submitted_enrollments_data = [
        (
            enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
            enrollment.session_exam.number_session,
            enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
            enrollment.score_final,
            _(enrollment.justification_final) if enrollment.justification_final else None,
        ) for enrollment in submitted_enrollments]
    table = message_config.create_table('submitted_enrollments',header_txt, submitted_enrollments_data)

    message_content = message_config.create_message_content(html_template_ref, txt_template_ref, [table], receivers, template_base_data, suject_data)
    return message_service.send_messages(message_content)

    # sent_error_message = None
    # txt_message_templates = {template.language: template for template in
    #                          list(message_template_mdl.find_by_reference('assessments_scores_submission_txt'))}
    # html_message_templates = {template.language: template for template in
    #                           list(message_template_mdl.find_by_reference('assessments_scores_submission_html'))}
    #
    # if not html_message_templates:
    #     sent_error_message = _('template_error').format('assessments_scores_submission_html')
    # else:
    #     submitted_enrollments_data = [
    #         (
    #             enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
    #             enrollment.session_exam.number_session,
    #             enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
    #             enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
    #             enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
    #             enrollment.score_final,
    #             _(enrollment.justification_final) if enrollment.justification_final else None,
    #         ) for enrollment in submitted_enrollments]
    #
    #     data = {
    #         'learning_unit_name': learning_unit_name,
    #         'signature': render_to_string('email/html_email_signature.html', {
    #             'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
    #             'logo_osis_url': LOGO_OSIS_URL})
    #     }
    #
    #     dest_by_lang = map_persons_by_languages(persons)
    #     for lang_code, person in dest_by_lang.items():
    #             if lang_code in html_message_templates:
    #                 html_message_template = html_message_templates.get(lang_code)
    #             else:
    #                 html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
    #             if lang_code in txt_message_templates:
    #                 txt_message_template = txt_message_templates.get(lang_code)
    #             else:
    #                 txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
    #             with translation.override(lang_code):
    #                 submitted_enrollment_header = (
    #                     _('acronym'),
    #                     _('sessionn'),
    #                     _('registration_number'),
    #                     _('lastname'),
    #                     _('firstname'),
    #                     _('score'),
    #                     _('documentation')
    #                 )
    #                 submitted_enrollments_table_html = render_table_template_as_string(
    #                     submitted_enrollment_header,
    #                     submitted_enrollments_data,
    #                     True
    #                 )
    #                 data['encoding_status'] = _('encoding_status_ended') if all_encoded else _('encoding_status_notended')
    #                 data['submitted_enrollments'] = submitted_enrollments_table_html
    #                 html_message = Template(html_message_template.template).render(Context(data))
    #                 subject = html_message_template.subject.format(learning_unit_name=learning_unit_name)
    #                 submitted_enrollments_table_txt = render_table_template_as_string(
    #                     submitted_enrollment_header,
    #                     submitted_enrollments_data,
    #                     False
    #                 )
    #                 data['submitted_enrollments'] = submitted_enrollments_table_txt
    #                 txt_message = Template(txt_message_template.template).render(Context(data))
    #                 send_and_save(persons=person,
    #                               subject=unescape(strip_tags(subject)),
    #                               message=unescape(strip_tags(txt_message)),
    #                               html_message=html_message, from_email=DEFAULT_FROM_EMAIL)
    # return sent_error_message


def send_mail_after_academic_calendar_changes(academic_calendar, offer_year_calendar, programm_managers):
    """
    Send an email to all the programme manager after changes has been made on a offer_year_calendar with customized
    = True
    :param academic_calendar:
    :param offer_year_calendar:
    :param programm_managers:
    :return un error message if the template does not exists.
    """

    html_template_ref = 'academic_calendar_changes_html'
    txt_template_ref = 'academic_calendar_changes_txt'
    receivers = [message_config.create_receiver(manager.person.id, manager.person.email, manager.person.language) for manager in programm_managers]
    suject_data = {'offer_year':            str(offer_year_calendar.offer_year.acronym),
                   'academic_calendar':     str(academic_calendar)}
    template_base_data = {
        'offer_year_title': offer_year_calendar.offer_year.title,
        'offer_year_acronym': offer_year_calendar.offer_year.acronym,
        'academic_calendar': str(academic_calendar),
    }
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref,
                                                            None, receivers, template_base_data, suject_data)

    return message_service.send_messages(message_content)
    # sent_error_message = None
    # txt_message_templates = {template.language: template for template in
    #                          list(message_template_mdl.find_by_reference('academic_calendar_changes_txt'))}
    # html_message_templates = {template.language: template for template in
    #                           list(message_template_mdl.find_by_reference('academic_calendar_changes_html'))}
    # if not html_message_templates:
    #     sent_error_message = _('template_error').format('academic_calendar_changes_html')
    # else:
    #     data = {
    #         'offer_year_title': offer_year_calendar.offer_year.title,
    #         'offer_year_acronym': offer_year_calendar.offer_year.acronym,
    #         'academic_calendar': str(academic_calendar),
    #         'signature': render_to_string('email/html_email_signature.html', {
    #             'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
    #             'logo_osis_url': LOGO_OSIS_URL})}
    #
    #     dest_by_lang = map_persons_by_languages([manager.person for manager in programm_managers
    #                                              if manager.person])
    #     for lang_code, persons in dest_by_lang.items():
    #         if lang_code in html_message_templates:
    #             html_message_template = html_message_templates.get(lang_code)
    #         else:
    #             html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
    #         if lang_code in txt_message_templates:
    #             txt_message_template = txt_message_templates.get(lang_code)
    #         else:
    #             txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
    #         with translation.override(lang_code):
    #             html_message = Template(html_message_template.template).render(Context(data))
    #             message = Template(txt_message_template.template).render(Context(data))
    #             subject = str(html_message_template.subject).format(offer_year=str(offer_year_calendar.offer_year.acronym),
    #                                                                 academic_calendar=str(academic_calendar))
    #             send_and_save(persons=persons,
    #                           subject=unescape(strip_tags(subject)),
    #                           message=unescape(strip_tags(message)),
    #                           html_message=html_message,
    #                           from_email=DEFAULT_FROM_EMAIL)
    # return sent_error_message


def send_message_after_all_encoded_by_manager(persons, enrollments, learning_unit_acronym, offer_acronym):
    """

    :param persons:
    :param enrollments:
    :param acronym:
    :return:
    """

    html_template_ref = 'assessments_all_scores_by_pgm_manager_html'
    txt_template_ref = 'assessments_all_scores_by_pgm_manager_txt'
    receivers = [message_config.create_receiver(person.id, person.email, person.language) for person in persons]
    suject_data = {
        'learning_unit_acronym': learning_unit_acronym,
        'offer_acronym':         offer_acronym
    }
    template_base_data = {
        'learning_unit_acronym':    learning_unit_acronym,
        'offer_acronym':            offer_acronym,
    }
    enrollments_data = [
        (
            enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
            enrollment.session_exam.number_session,
            enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
            enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
            enrollment.score_final,
            _(enrollment.justification_final) if enrollment.justification_final else None,
        ) for enrollment in enrollments]
    enrollments_headers = (
        'acronym',
        'sessionn',
        'registration_number',
        'lastname',
        'firstname',
        'score',
        'documentation'
    )
    table = message_config.create_table('enrollments', enrollments_headers, enrollments_data)
    message_content = message_config.create_message_content(html_template_ref, txt_template_ref,
                                                            [table], receivers, template_base_data, suject_data)
    return message_service.send_messages(message_content)

    # txt_message_templates = {template.language: template for template in
    #                          list(message_template_mdl.find_by_reference('assessments_all_scores_by_pgm_manager_txt'))}
    # html_message_templates = {template.language: template for template in
    #                           list(message_template_mdl.find_by_reference('assessments_all_scores_by_pgm_manager_html'))}
    #
    # enrollments_data = [
    #     (
    #         enrollment.learning_unit_enrollment.offer_enrollment.offer_year.acronym,
    #         enrollment.session_exam.number_session,
    #         enrollment.learning_unit_enrollment.offer_enrollment.student.registration_id,
    #         enrollment.learning_unit_enrollment.offer_enrollment.student.person.last_name,
    #         enrollment.learning_unit_enrollment.offer_enrollment.student.person.first_name,
    #         enrollment.score_final,
    #         _(enrollment.justification_final) if enrollment.justification_final else None,
    #     ) for enrollment in enrollments]
    #
    # data = {
    #     'learning_unit_acronym': learning_unit_acronym,
    #     'offer_acronym': offer_acronym,
    #     'signature': render_to_string('email/html_email_signature.html', {
    #         'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
    #         'logo_osis_url': LOGO_OSIS_URL})
    # }
    # dest_by_lang = map_persons_by_languages(persons)
    # for lang_code, person in dest_by_lang.items():
    #     if lang_code in html_message_templates:
    #         html_message_template = html_message_templates.get(lang_code)
    #     else:
    #         html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
    #     if not html_message_template:
    #         sent_error_message = _('template_error').format('assessments_all_scores_by_pgm_manager_html')
    #         return sent_error_message
    #
    #     if lang_code in txt_message_templates:
    #         txt_message_template = txt_message_templates.get(lang_code)
    #     else:
    #         txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
    #     with translation.override(lang_code):
    #         enrollments_header = (
    #             _('acronym'),
    #             _('sessionn'),
    #             _('registration_number'),
    #             _('lastname'),
    #             _('firstname'),
    #             _('score'),
    #             _('documentation')
    #         )
    #         enrollments_table_html = render_table_template_as_string(
    #             enrollments_header,
    #             enrollments_data,
    #             True
    #         )
    #         data['enrollments'] = enrollments_table_html
    #         html_message = Template(html_message_template.template).render(Context(data))
    #         subject = html_message_template.subject.format(learning_unit_acronym=learning_unit_acronym,
    #                                                        offer_acronym=offer_acronym)
    #         enrollments_table_txt = render_table_template_as_string(
    #             enrollments_header,
    #             enrollments_data,
    #             False
    #         )
    #         data['enrollments'] = enrollments_table_txt
    #         txt_message = Template(txt_message_template.template).render(Context(data))
    #         send_and_save(persons=person,
    #                       subject=unescape(strip_tags(subject)),
    #                       message=unescape(strip_tags(txt_message)),
    #                       html_message=html_message, from_email=DEFAULT_FROM_EMAIL)
    # return None


def send_again(message_history_id):
    """
    send a message from message history again
    :param message_history_id The id of the message history to send again
    :return the sent message

    TO-DO : correction of send_message in osis-common to get the associated receiver , based on id and receiver model

    """
    message_history = message_history_mdl.find_by_id(message_history_id)
    person = person_mdl.find_by_id(message_history.receiver_id)
    if person:
        receiver = message_config.create_receiver(person.id, person.email, person.language)
        return message_service.send_again(receiver, message_history_id)
    else:
        return _('no_receiver_error')
