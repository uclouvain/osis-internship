
from io import BytesIO
from io import StringIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate,SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table,TableStyle,Frame,PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape

from core.models import AcademicCalendar, SessionExam, ExamEnrollment, LearningUnitYear, Person, AcademicYear

PAGE_SIZE = A4
MARGIN_SIZE = 25 * mm

def print_notes(request,tutor, academic_year, session_exam,sessions,learning_unit_year_id):
    print('zut', str(learning_unit_year_id), ' zut session exam : ' ,str(session_exam.id) )

    """
    Create a multi-page document
    """

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=landscape(PAGE_SIZE),
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=18)


    # doc = BaseDocTemplate(buffer, pagesize=PAGE_SIZE)
    # frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
    #                id='normal')
    # template = PageTemplate(id='test', frames=frame, onPage=footer)
    # doc.addPageTemplates([template])
    #
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    Contenu = []

    academic_calendar = AcademicCalendar.find_academic_calendar_by_event_type(academic_year.id,session_exam.number_session)
    Contenu.append(Paragraph("<font size=12>Responsable : %s</font>" % tutor, styles["Normal"]) )
    Contenu.append(Paragraph('<font size=12>Année académique : %s</font>' % str(academic_year.year), styles["Normal"]))
    Contenu.append(Paragraph('<font size=12>Session : %d</font>' % session_exam.number_session, styles["Normal"]))

    Contenu.append(Spacer(1, 12))
    data =[]
    data.append(['Année académique',
              'Session',
              'Code cours',
              'Programme',
              'Noma',
              'Nom',
              'Prénom',
              'Note chiffrée',
              'Autre note',
              'Date de remise'])

    for rec_exam_enrollment in ExamEnrollment.find_exam_enrollments(session_exam.id):
        print('zut : ', str(rec_exam_enrollment.learning_unit_enrollment.learning_unit_year.id))
        if (int(rec_exam_enrollment.learning_unit_enrollment.learning_unit_year.id) == int(learning_unit_year_id)) or int(learning_unit_year_id) == -1:
            student = rec_exam_enrollment.learning_unit_enrollment.student
            o = rec_exam_enrollment.learning_unit_enrollment.offer
            person = Person.find_person(student.person.id)
            data.append([str(academic_year),
                           str(session_exam.number_session),
                           session_exam.learning_unit_year.acronym,
                           o.acronym,
                           student.registration_id,
                           person.last_name,
                           person.first_name,
                           rec_exam_enrollment.score,
                           rec_exam_enrollment.justification,
                           academic_calendar.end_date.strftime('%d/%m/%Y')
                           ])



    t=Table(data)
    t.setStyle(TableStyle([
                       ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                       ]))


    Contenu.append(t)

    doc.build(Contenu, onFirstPage=addHeaderFooter, onLaterPages=addHeaderFooter)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def addHeaderFooter(canvas, doc):
    """
    Add the page number
    """
    styles = getSampleStyleSheet()
    # Save the state of our canvas so we can draw on it
    canvas.saveState()

    # Header
    header_building(canvas,doc)
    # Footer
    footer_building(canvas, doc,styles)

    # Release the canvas
    canvas.restoreState()



def header_building(canvas, doc):
    #todo ne plus écrire en dur localhost
    a = Image("http://localhost:8000"+settings.STATIC_URL + "images/logo_osis.png")

    data_header=[[a,'Université Catholique Louvain',''],
                 ['','Louvain-la-Neuve','Feuille de notes'],
                 ['','Belgique','']]
    t_header=Table(data_header, [40*mm, 100*mm,100*mm])
    t_header.setStyle(TableStyle([
                       ('SPAN',(0,0), (0,-1)),
                       ]))
    w, h = t_header.wrap(doc.width, doc.topMargin)
    t_header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)


def footer_building(canvas, doc,styles):
    page_num = canvas.getPageNumber()
    footer = Paragraph('Footer' + 'Page #%s' % page_num, styles['Normal'])
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin, h)
