from base.utils.send_mail import *
from django.template.loader import render_to_string
from backoffice import settings
from django.template import Template, Context


def send_mail_to_teacher_new_dissert(adviser):
    """
    Notify (for the teacher) of a new dissertation project
    """
    sent_error_message = None
    txt_message_templates = {template.language: template for template in
                             list(message_template_mdl.find_by_reference(
                                 'dissertation_adviser_new_project_dissertation_txt'))}

    html_message_templates = {template.language: template for template in
                              list(message_template_mdl.find_by_reference(
                                  'dissertation_adviser_new_project_dissertation_html'))}
    if not html_message_templates:
        sent_error_message = 'template_error'.format('dissertation_adviser_new_project_dissertation_html')
    else:
        data = {
            'adviser': adviser,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})}
        persons = [adviser.person]
        dest_by_lang = map_persons_by_languages(persons)

        for lang_code, persons in dest_by_lang.items():
            if lang_code in html_message_templates:
                html_message_template = html_message_templates.get(lang_code)
            else:
                html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
            if lang_code in txt_message_templates:
                txt_message_template = txt_message_templates.get(lang_code)
            else:
                txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
            with translation.override(lang_code):
                html_message = Template(html_message_template.template).render(Context(data))
                message = Template(txt_message_template.template).render(Context(data))
                subject = str(html_message_template.subject)

                send_and_save(persons=persons,
                              subject=unescape(strip_tags(subject)),
                              message=unescape(strip_tags(message)),
                              html_message=html_message,
                              from_email=DEFAULT_FROM_EMAIL)

    return sent_error_message


def send_mail_dissert_accepted_by_teacher(person):
    """
    Notify (for the student) dissertation accepted by teacher
    """
    sent_error_message = None
    txt_message_templates = {template.language: template for template in
                             list(message_template_mdl.find_by_reference('dissertation_accepted_by_teacher_txt'))}

    html_message_templates = {template.language: template for template in
                              list(message_template_mdl.find_by_reference('dissertation_accepted_by_teacher_html'))}
    if not html_message_templates:
        sent_error_message = 'template_error'.format('dissertation_accepted_by_teacher_html')
    else:
        data = {
            'person': person,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})}
        persons = [person]

        dest_by_lang = map_persons_by_languages(persons)

        for lang_code, persons in dest_by_lang.items():
            if lang_code in html_message_templates:
                html_message_template = html_message_templates.get(lang_code)
            else:
                html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
            if lang_code in txt_message_templates:
                txt_message_template = txt_message_templates.get(lang_code)
            else:
                txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
            with translation.override(lang_code):
                html_message = Template(html_message_template.template).render(Context(data))
                message = Template(txt_message_template.template).render(Context(data))
                subject = str(html_message_template.subject)

                send_and_save(persons=persons,
                              subject=unescape(strip_tags(subject)),
                              message=unescape(strip_tags(message)),
                              html_message=html_message,
                              from_email=DEFAULT_FROM_EMAIL)

    return sent_error_message


def send_mail_dissert_refused_by_teacher(person):
    """
    Notify (for the student) dissertation accepted by teacher
    """
    sent_error_message = None
    txt_message_templates = {template.language: template for template in
                             list(message_template_mdl.find_by_reference('dissertation_refused_by_teacher_txt'))}

    html_message_templates = {template.language: template for template in
                              list(message_template_mdl.find_by_reference('dissertation_refused_by_teacher_html'))}
    if not html_message_templates:
        sent_error_message = 'template_error'.format('dissertation_refused_by_teacher_html')
    else:
        data = {
            'person': person,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})}
        persons = [person]

        dest_by_lang = map_persons_by_languages(persons)

        for lang_code, persons in dest_by_lang.items():
            if lang_code in html_message_templates:
                html_message_template = html_message_templates.get(lang_code)
            else:
                html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
            if lang_code in txt_message_templates:
                txt_message_template = txt_message_templates.get(lang_code)
            else:
                txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
            with translation.override(lang_code):
                html_message = Template(html_message_template.template).render(Context(data))
                message = Template(txt_message_template.template).render(Context(data))
                subject = str(html_message_template.subject)

                send_and_save(persons=persons,
                              subject=unescape(strip_tags(subject)),
                              message=unescape(strip_tags(message)),
                              html_message=html_message,
                              from_email=DEFAULT_FROM_EMAIL)
    return sent_error_message


def send_mail_dissert_acknowledgement(person):
    """
    Notify (for the student) dissertation accepted by teacher
    """
    sent_error_message = None
    txt_message_templates = {template.language: template for template in
                             list(message_template_mdl.find_by_reference('dissertation_acknowledgement_txt'))}

    html_message_templates = {template.language: template for template in
                              list(message_template_mdl.find_by_reference('dissertation_acknowledgement_html'))}
    if not html_message_templates:
        sent_error_message = 'template_error'.format('dissertation_acknowledgement_html')
    else:
        data = {
            'person': person,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})}
        persons = [person]

        dest_by_lang = map_persons_by_languages(persons)

        for lang_code, persons in dest_by_lang.items():
            if lang_code in html_message_templates:
                html_message_template = html_message_templates.get(lang_code)
            else:
                html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
            if lang_code in txt_message_templates:
                txt_message_template = txt_message_templates.get(lang_code)
            else:
                txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
            with translation.override(lang_code):
                html_message = Template(html_message_template.template).render(Context(data))
                message = Template(txt_message_template.template).render(Context(data))
                subject = str(html_message_template.subject)

                send_and_save(persons=persons,
                              subject=unescape(strip_tags(subject)),
                              message=unescape(strip_tags(message)),
                              html_message=html_message,
                              from_email=DEFAULT_FROM_EMAIL)

    return sent_error_message


def send_mail_dissert_refused_by_com(person_student,person_teacher):
    """
    Notify (for the student) dissertation accepted by teacher
    """
    sent_error_message = None
    txt_message_templates = {template.language: template for template in
                             list(message_template_mdl.find_by_reference('dissertation_refused_by_com_txt'))}

    html_message_templates = {template.language: template for template in
                              list(message_template_mdl.find_by_reference('dissertation_refused_by_com_html'))}
    if not html_message_templates:
        sent_error_message = 'template_error'.format('dissertation_refused_by_com_html')
    else:
        persons = [person_student, person_teacher]
        data = {
            'persons': persons,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})}


        dest_by_lang = map_persons_by_languages(persons)

        for lang_code, persons in dest_by_lang.items():
            if lang_code in html_message_templates:
                html_message_template = html_message_templates.get(lang_code)
            else:
                html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
            if lang_code in txt_message_templates:
                txt_message_template = txt_message_templates.get(lang_code)
            else:
                txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
            with translation.override(lang_code):
                html_message = Template(html_message_template.template).render(Context(data))
                message = Template(txt_message_template.template).render(Context(data))
                subject = str(html_message_template.subject)

                send_and_save(persons=persons,
                              subject=unescape(strip_tags(subject)),
                              message=unescape(strip_tags(message)),
                              html_message=html_message,
                              from_email=DEFAULT_FROM_EMAIL)

    return sent_error_message


def send_mail_dissert_accepted_by_com(person_student):
    """
    Notify (for the student) dissertation accepted by teacher
    """
    sent_error_message = None
    txt_message_templates = {template.language: template for template in
                             list(message_template_mdl.find_by_reference('dissertation_accepted_by_com_txt'))}

    html_message_templates = {template.language: template for template in
                              list(message_template_mdl.find_by_reference('dissertation_accepted_by_com_html'))}
    if not html_message_templates:
        sent_error_message = 'template_error'.format('dissertation_accepted_by_com_html')
    else:
        persons = [person_student]

        data = {
            'persons': persons,
            'signature': render_to_string('email/html_email_signature.html', {
                'logo_mail_signature_url': LOGO_EMAIL_SIGNATURE_URL,
                'logo_osis_url': LOGO_OSIS_URL})}

        dest_by_lang = map_persons_by_languages(persons)

        for lang_code, persons in dest_by_lang.items():
            if lang_code in html_message_templates:
                html_message_template = html_message_templates.get(lang_code)
            else:
                html_message_template = html_message_templates.get(settings.LANGUAGE_CODE)
            if lang_code in txt_message_templates:
                txt_message_template = txt_message_templates.get(lang_code)
            else:
                txt_message_template = txt_message_templates.get(settings.LANGUAGE_CODE)
            with translation.override(lang_code):
                html_message = Template(html_message_template.template).render(Context(data))
                message = Template(txt_message_template.template).render(Context(data))
                subject = str(html_message_template.subject)

                send_and_save(persons=persons,
                              subject=unescape(strip_tags(subject)),
                              message=unescape(strip_tags(message)),
                              html_message=html_message,
                              from_email=DEFAULT_FROM_EMAIL)

    return sent_error_message
