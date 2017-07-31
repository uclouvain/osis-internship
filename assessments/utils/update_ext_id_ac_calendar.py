from base.models import session_exam_calendar, academic_calendar, offer_year_calendar

map_assoc_english_french = {
    'Submission of exam scores - exam session 1': "Encodages des notes - Session d'examens n°1",
    'Submission of exam scores - exam session 2': "Encodages des notes - Session d'examens n°2",
    'Submission of exam scores - exam session 3': "Encodages des notes - Session d'examens n°3",
    'Deliberations - exam session 1': "Délibérations - Session d'examens n°1",
    'Deliberations - exam session 2': "Délibérations - Session d'examens n°2",
    'Deliberations - exam session 3': "Délibérations - Session d'examens n°3",
    'Diffusion of exam scores - exam session 1': "Diffusion des notes - Session d'examens n°1",
    'Diffusion of exam scores - exam session 2': "Diffusion des notes - Session d'examens n°2",
    'Diffusion of exam scores - exam session 3': "Diffusion des notes - Session d'examens n°3",
    'Exam enrollments - exam session 1': "Inscriptions aux examens - Session d'examens n°1",
    'Exam enrollments - exam session 2': "Inscriptions aux examens - Session d'examens n°2",
    'Exam enrollments - exam session 3': "Inscriptions aux examens - Session d'examens n°3",
    'Teaching charge application': 'Candidature en ligne',
}


def execute():
    _remove_unused_academic_calendars()
    number_session_mapped_with_academic_cal = {sess_exam.academic_calendar_id: sess_exam.number_session
                                               for sess_exam in session_exam_calendar.SessionExamCalendar.objects.all()}
    _update_external_id_academic_calendars(number_session_mapped_with_academic_cal)
    _update_external_id_offer_year_calendars(number_session_mapped_with_academic_cal)


def _remove_unused_academic_calendars():
    for academic_cal in academic_calendar.AcademicCalendar.objects.all():
        if not academic_cal.reference:
            title = academic_cal.title
            academic_cal.delete()
            print('Academic calendar "{}" was removed.'.format(title))


def _update_external_id_academic_calendars(number_session_mapped_with_academic_cal):
    for academic_cal in academic_calendar.AcademicCalendar.objects.all():
        print("Old external_id = '{}'".format(academic_cal.external_id))
        new_external_id = '{}_{}_{}'.format(number_session_mapped_with_academic_cal.get(academic_cal.id),
                                            academic_cal.reference,
                                            academic_cal.academic_year.year)
        academic_cal.external_id = new_external_id
        title_in_french = map_assoc_english_french.get(academic_cal.title)
        if title_in_french:
            academic_cal.title = title_in_french
        academic_cal.save(functions=[])
        print("New external_id saved = '{}'".format(academic_cal.external_id))


def _update_external_id_offer_year_calendars(number_session_mapped_with_academic_cal):
    for off_cal in offer_year_calendar.OfferYearCalendar.objects.all():
        print("Old OfferYearCalendar external_id = '{}'".format(off_cal.external_id))
        ext_id_values = off_cal.external_id.split('_')
        number_session = number_session_mapped_with_academic_cal.get(off_cal.academic_calendar_id)
        reference = off_cal.academic_calendar.reference
        new_external_id = '{}_{}_{}_{}'.format(ext_id_values[0], ext_id_values[1], number_session, reference)
        off_cal.external_id = new_external_id
        off_cal.save()
        print("New OfferYearCalendar external_id saved = '{}'".format(off_cal.external_id))
