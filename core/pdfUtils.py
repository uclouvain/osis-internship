
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

def pdf_test(request,tutor, academic_year, session_exam,sessions):

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
    #
    # logo = "static/images/logo_osis.png"
    # im = Image(logo, 2*inch, 2*inch)
    # Contenu.append(im)

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

    for rec_exam_enrollment in ExamEnrollment.find_exam_enrollments(session_exam):
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
    page_num = canvas.getPageNumber()
    # text = "Page #%s" % page_num
    # canvas.drawRightString(200*mm, 20*mm, text)

    # Save the state of our canvas so we can draw on it
    canvas.saveState()
    #todo ajouter le logo



    styles = getSampleStyleSheet()


    # Header
    header_lines="<b>Université Catholique Louvain</b>"
    header_lines += "<br/>"
    header_lines += "Louvain-la-Neuve"
    header_lines += "<br/>"
    header_lines += "Belgique"
    header_lines += "<br/>"
    header_lines += "http://www.uclouvain.be"
    header = Paragraph(header_lines, styles['Normal'])
    w, h = header.wrap(doc.width, doc.topMargin)
    header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)
    # Footer

    footer_text = 'Footer' + 'Page #%s' % page_num


    footer = Paragraph(footer_text, styles['Normal'])
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin, h)

    # Release the canvas
    canvas.restoreState()
