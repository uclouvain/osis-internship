##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.utils.translation import ungettext
from openpyxl import load_workbook
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from base.forms import ScoreFileForm
from base import models as mdl
from base.utils import export_utils


@login_required
def upload_scores_file(request, learning_unit_id,tutor_id):
    message_validation = ""
    if request.method == 'POST':
        form = ScoreFileForm(request.POST, request.FILES)
        if form.is_valid():
            file_name = request.FILES['file']
            if file_name is not None:
                if ".xls" not in str(file_name):
                    message_validation = _('file_must_be_xls')
                else:
                    is_valid = __save_xls_scores(request, file_name)
                    if not is_valid:
                        message_validation = '%s' % _('invalid_file')

                messages.add_message(request, messages.INFO, '%s' % message_validation)

                return HttpResponseRedirect(reverse('online_encoding', args=[learning_unit_id,tutor_id]))
        else:
            return HttpResponseRedirect(reverse('online_encoding', args=[learning_unit_id,tutor_id]))


def __save_xls_scores(request, file_name):
    print('__save_xls_scores')
    wb = load_workbook(file_name, read_only=True)
    ws = wb.active
    nb_row = 0
    is_valid = True
    validation_error = ""
    data_line_number = 1
    new_scores_number = 0
    new_scores = False
    session_exam = None
    for row in ws.rows:

        new_score = False
        if nb_row > 0 and is_valid:
            student = mdl.student.find_by_registration_id(row[4].value)
            info_line = "%s %d :" % (_('Line'),data_line_number)
            if not student:
                validation_error += "%s %s!" % (info_line, _('student_not_exist') % (str(row[4].value)))
            else:
                academic_year = mdl.academic_year.find_academic_year_by_year(int(row[0].value[:4]))
                if not academic_year:
                    validation_error += "%s %s!" % (info_line, _('academic_year_not_exist') % (row[0].value))
                else:
                    offer_year = mdl.offer_year.find_by_academicyear_acronym(academic_year, row[3].value)
                    if  not offer_year :
                        validation_error += "%s %s!" % (info_line, _('offer_year_not_exist') % (str(row[3].value), academic_year.year))
                    else:

                        offer_enrollment = mdl.offer_enrollment.find_by_student_offer(student, offer_year)
                        if not offer_enrollment :
                            validation_error += "%s %s!" % (info_line, _('offer_enrollment_not_exist'))
                        else:
                            learning_unit_year_lists = mdl.learning_unit_year.search(academic_year,
                                                                                     row[2].value)
                            if len(learning_unit_year_lists) == 1:
                                learning_unit_year = learning_unit_year_lists[0]
                            if not learning_unit_year:
                                validation_error += "%s %s!" % (info_line, _('activity_not_exit') % (str(row[2].value)))
                            else:
                                learning_unit_enrollment = mdl.learning_unit_enrollment.find_by_learningunit_enrollment(learning_unit_year, offer_enrollment)
                                if not learning_unit_enrollment:
                                    validation_error += "%s %s!" % (info_line, _('enrollment_activity_not_exist') % (str(row[2].value)))
                                else:
                                    session_number = int(row[1].value)
                                    exam_enrollment = mdl.exam_enrollment.find_by_enrollment_session(learning_unit_enrollment, session_number)
                                    if session_exam is None:
                                        session_exam = exam_enrollment.session_exam
                                    if exam_enrollment.encoding_status != 'SUBMITTED':
                                        if row[7].value is None:
                                            note = None
                                        else:
                                            note = float(row[7].value)
                                        note_valide = True
                                        if not note is None:
                                            if note<0 or note>20:
                                                validation_error += "%s %s!" % (info_line, _('scores_gt_0_lt_20'))
                                                note_valide = False
                                            else:
                                                if not learning_unit_year is None and not learning_unit_year.decimal_scores and round(note) != note:
                                                    validation_error += "%s %s!" % (info_line, _('score_decimal_not_allowed'))
                                                    note_valide = False
                                        else:
                                            note_valide = False
                                        # attention dans le xsl les choix pour la justification sont des libellés pas
                                        # les valeurs BD
                                        justification_xls = None
                                        if row[8].value:
                                            for k, v in dict(mdl.exam_enrollment.JUSTIFICATION_TYPES).items():
                                                if v.lower() == str(row[8].value.lower()):
                                                    justification_xls=k
                                        justification_valide=True
                                        if not note is None and (not justification_xls is None and not justification_xls=='CHEATING'):
                                            note_valide = False
                                            justification_valide=False
                                            validation_error += "%s %s!" % (info_line, _('constraint_score_other_score'))

                                        if note_valide:
                                            if exam_enrollment.score_final != note:
                                                new_scores_number = new_scores_number + 1
                                                new_scores = True
                                                new_score=True

                                            exam_enrollment.score_final = note

                                        if justification_valide and not justification_xls is None and exam_enrollment.justification_final != justification_xls:
                                            new_scores_number = new_scores_number + 1
                                            new_scores = True
                                            new_score=True
                                            exam_enrollment.justification_final = justification_xls

                                        if new_score :
                                            exam_enrollment.encoding_status = 'SUBMITTED'
                                            exam_enrollment.score_draft = note
                                            exam_enrollment.justification_draft = justification_xls
                                            exam_enrollment.save()
                                            mdl.exam_enrollment.create_exam_enrollment_historic(request.user,
                                                                                                exam_enrollment,note,
                                                                                                justification_xls)

            data_line_number=data_line_number+1
        else:
            #Il faut valider le fichier xls
            #Je valide les entêtes de colonnes
            list_header = export_utils.HEADER

            i = 0
            for header_col in list_header:
                if str(row[i].value) != header_col:
                    is_valid = False
                    break
                i = i +1
            new_scores_number=0

        nb_row = nb_row + 1

    messages.add_message(request, messages.WARNING, validation_error)
    if session_exam is not None:
        all_encoded = True
        enrollments = mdl.exam_enrollment.find_exam_enrollments_by_session(session_exam)
        for enrollment in enrollments:
            if not enrollment.score_final and not enrollment.justification_final:
                all_encoded = False

        if all_encoded:
            session_exam.status = 'CLOSED'
            session_exam.save()

    if new_scores :
        if new_scores_number > 0:
            count = new_scores_number
            text = ungettext(
                '%(count)d %(name)s.',
                '%(count)d %(plural_name)s.',
                count
            ) % {
                'count': new_scores_number,
                'name': _('score_injected'),
                'plural_name':  _('scores_injected')
            }

            messages.add_message(request, messages.INFO, '%s' % text)
    else:
        if is_valid:
            messages.add_message(request, messages.INFO, '%s' % _('no_score_injected'))

    return is_valid


@login_required
def upload_scores_file_pgmer(request, learning_unit_id):
    return upload_scores_file(request,learning_unit_id,None)