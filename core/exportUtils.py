from django.http import HttpResponse

import openpyxl
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from openpyxl.cell import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import Fill, Color, Style, PatternFill
from openpyxl.worksheet import Worksheet, ColumnDimension, RowDimension

from core.models import AcademicCalendar, SessionExam, ExamEnrollment, LearningUnitYear, Person, AcademicYear

from django.utils.dateformat import DateFormat
from django.utils.formats import get_format

def export_xls(request,session_id,learning_unit_year_id,academic_year_id):
    academic_year = AcademicYear.find_academic_year(academic_year_id)
    session_exam = SessionExam.current_session_exam()
    academic_calendar = AcademicCalendar.find_academic_calendar_by_event_type(academic_year_id,session_exam.number_session)

    wb = Workbook()
    ws = wb.active

    __columns_ajusting(ws)

# masquage de la colonne avec l'id exam enrollment


    header = ['Année académique',
              'Session',
              'Code cours',
              'Programme',
              'Noma',
              'Nom',
              'Prénom',
              'Note chiffrée',
              'Autre note',
              'Date de remise',
              'ID']
    ws.append(header)

    dv = __create_data_list_for_justification()
    ws.add_data_validation(dv)

    cptr=1
    for rec_exam_enrollment in ExamEnrollment.find_exam_enrollments(session_exam):
        student = rec_exam_enrollment.learning_unit_enrollment.student
        o = rec_exam_enrollment.learning_unit_enrollment.offer
        person = Person.find_person(student.person.id)

        ws.append([str(academic_year),
                   str(session_exam.number_session),
                   session_exam.learning_unit_year.acronym,
                   o.acronym,
                   student.registration_id,
                   person.last_name,
                   person.first_name,
                   rec_exam_enrollment.score,
                   rec_exam_enrollment.justification,
                   academic_calendar.end_date.strftime('%d/%m/%Y'),
                   rec_exam_enrollment.id
                   ])


        cptr = cptr+1
        __coloring_non_editable(ws,cptr)


    dv.ranges.append('I2:I'+str(cptr+100))#Ajouter 100 pour si on ajoute des enregistrements

    response = HttpResponse(content=save_virtual_workbook(wb))
    response['Content-Disposition'] = 'attachment; filename=myexport.xlsx'
    response['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response


def __columns_ajusting(ws):
    """
    ajustement des colonnes à la bonne dimension
    :param ws:
    :return:
    """
    col_academic_year = ws.column_dimensions['A']
    col_academic_year.width = 18
    col_last_name = ws.column_dimensions['F']
    col_last_name.width = 30
    col_first_name = ws.column_dimensions['G']
    col_first_name.width = 30
    col_note = ws.column_dimensions['H']
    col_note.width = 20
    col_id_exam_enrollment = ws.column_dimensions['K']
    col_id_exam_enrollment.hidden = True


def  __create_data_list_for_justification():
    """
    Création de la liste de choix pour la justification
    :return:
    """
    dv = DataValidation(type="list", formula1='"ABSENT,CHEATING,ILL,JUSTIFIED_ABSENCE,SCORE_MISSING"', allow_blank=True)
    dv.error ='Votre entrée n\'est pas dans la liste'
    dv.errorTitle = 'Entrée invalide'

    dv.prompt = 'Merci de sélectionner dans la liste'
    dv.promptTitle = 'Liste de sélection'
    return dv


def __coloring_non_editable(ws,cptr):
    """
    définition du style pour les colonnes qu'on ne doit pas modifier
    :return:
    """
    style_no_modification = Style(fill=PatternFill(patternType='solid', fgColor=Color('C1C1C1')))

    # coloration des colonnes qu'on ne doit pas modifier
    i=1
    while i < 11:
        if i< 8 or i>9:
            ws.cell(row=cptr, column=i).style = style_no_modification
        i=i+1
