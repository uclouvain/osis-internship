from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from core.models import AcademicCalendar, SessionExam, ExamEnrollment, LearningUnitYear, Person, AcademicYear

def export_xls(request,session_id,learning_unit_year_id,academic_year_id):
    academic_year = AcademicYear.find_academic_year(academic_year_id)
    session_exam = SessionExam.current_session_exam()
    academic_calendar = AcademicCalendar.find_academic_calendar_by_event_type(academic_year_id,session_exam.number_session)

    wb = Workbook()
    ws = wb.active

    header = ['Academic year',
              'Session',
              'Activity',
              'Offer',
              'Section',
              'Registration_number',
              'Lastname',
              'Firstname',
              'Score_final',
              'Justification_final',
              'End_date']
    ws.append(header)

    for rec_exam_enrollment in ExamEnrollment.find_exam_enrollments(session_exam):
        student = rec_exam_enrollment.learning_unit_enrollment.student
        o = rec_exam_enrollment.learning_unit_enrollment.offer
        person = Person.find_person(student.person.id)

        ws.append([str(academic_year),
                   str(session_exam.number_session),
                   session_exam.learning_unit_year.acronym,
                   o.acronym,
                   "?",
                   student.registration_id,
                   person.last_name,
                   person.first_name,
                   rec_exam_enrollment.score,
                   rec_exam_enrollment.justification,
                   academic_calendar.end_date
                   ])

    response = HttpResponse(content=save_virtual_workbook(wb))
    response['Content-Disposition'] = 'attachment; filename=myexport.xlsx'
    response['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    return response
