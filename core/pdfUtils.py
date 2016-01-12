
from io import BytesIO
from io import StringIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings

from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER
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
    """
    Create a multi-page document
    """

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="feuillesNotes.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=PAGE_SIZE,
                            rightMargin=72,
                            leftMargin=72,
                            topMargin=72,
                            bottomMargin=18)


    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    Contenu = []
#critères
    academic_calendar = AcademicCalendar.find_academic_calendar_by_event_type(academic_year.id,session_exam.number_session)

    if learning_unit_year_id != -1 :
        list_exam_enrollment = ExamEnrollment.find_exam_enrollments(session_exam)
    else:
        if tutor:
            sessions = SessionExam.find_sessions_by_tutor(tutor, academic_year, session_exam)
        # In case the user is not a tutor we check whether it is member of a faculty.
        elif request.user.groups.filter(name='FAC').exists():
            faculty = ProgrammeManager.find_faculty_by_user(request.user)
            if faculty:
                sessions = SessionExam.find_sessions_by_faculty(faculty, academic_year, session_exam)

        # Calculate the progress of all courses of the tutor.
        list_exam_enrollment = []
        for session in sessions:
            enrollments = list(ExamEnrollment.find_exam_enrollments(session.id))
            if enrollments:
                list_exam_enrollment = list_exam_enrollment + enrollments


    list_notes_building(session_exam, learning_unit_year_id, academic_year, academic_calendar, tutor, list_exam_enrollment, styles, Contenu)



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
    header_building(canvas,doc, styles)
    # Footer
    footer_building(canvas, doc,styles)

    # Release the canvas
    canvas.restoreState()


def header_building(canvas, doc,styles):
    a = Image("core/static/images/logo_institution.jpg")
    P = Paragraph('''
                    <para align=center spaceb=3>
                        <font size=16>Feuille de notes</font>
                    </para>''',
       styles["BodyText"])
    data_header=[[a,'Université Catholique Louvain\nLouvain-la-Neuve\nBelgique',P],]

    t_header=Table(data_header, [30*mm, 100*mm,50*mm])

    t_header.setStyle(TableStyle([
                    #    ('SPAN',(0,0), (0,-1)),
                       ]))
    w, h = t_header.wrap(doc.width, doc.topMargin)
    t_header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)


def footer_building(canvas, doc,styles):
    page_num = canvas.getPageNumber()
    footer = Paragraph('Footer' + 'Page #%s' % page_num, styles['Normal'])
    w, h = footer.wrap(doc.width, doc.bottomMargin)
    footer.drawOn(canvas, doc.leftMargin, h)


def list_notes_building(session_exam, learning_unit_year_id, academic_year, academic_calendar, tutor,list_exam_enrollment, styles, Contenu):
#liste des notes
    Contenu.append(Spacer(1, 12))
    data = headers_table()

    old_pgm = None
    current_learning_unit_year= None
    for rec_exam_enrollment in list_exam_enrollment:
        print('for')
        if (int(rec_exam_enrollment.learning_unit_enrollment.learning_unit_year.id) == int(learning_unit_year_id)) or int(learning_unit_year_id) == -1:
            print('if')
            student = rec_exam_enrollment.learning_unit_enrollment.student
            o = rec_exam_enrollment.learning_unit_enrollment.offer
            if old_pgm is None:
                old_pgm = o
                current_learning_unit_year = rec_exam_enrollment.learning_unit_enrollment.learning_unit_year
            if o != old_pgm:
                #Autre programme - 1. mettre les critères
                main_data(tutor, academic_year, session_exam, styles, current_learning_unit_year,old_pgm, Contenu)
                #Autre programme - 2. il faut écrire le tableau

                t=Table(data,[30*mm,30*mm,30*mm,30*mm,30*mm,30*mm])
                t.setStyle(TableStyle([
                                   ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,0), (-1,-1), 'TOP')
                                   ]))


                Contenu.append(t)
                #Autre programme - 3. Imprimer légende
                end_page_infos_building(Contenu, styles)
                legend_building(Contenu, styles)
                #Autre programme - 4. il faut faire un saut de page
                Contenu.append(PageBreak())
                data = headers_table()
                old_pgm =o
                current_learning_unit_year = rec_exam_enrollment.learning_unit_enrollment.learning_unit_year
                #

            person = Person.find_person(student.person.id)
            data.append([student.registration_id,
                           person.last_name,
                           person.first_name,
                           rec_exam_enrollment.score,
                           rec_exam_enrollment.justification,
                           academic_calendar.end_date.strftime('%d/%m/%Y')
                           ])


    if old_pgm is None:
        pass
    else:
        main_data(tutor, academic_year, session_exam, styles,current_learning_unit_year, old_pgm, Contenu)
        t=Table(data,[30*mm,30*mm,30*mm,30*mm,30*mm,30*mm])
        t.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           ]))


        Contenu.append(t)
        end_page_infos_building(Contenu, styles)
        legend_building(Contenu, styles)


def legend_building(Contenu, styles):
    Contenu.append(Spacer(1, 30))
    p = ParagraphStyle('legend')
    p.textColor = 'grey'
    p.borderColor = 'grey'
    p.borderWidth = 1
    p.alignment = TA_CENTER
    p.fontSize = 10
    p.borderPadding = 5
    Contenu.append(Paragraph("Légende pour le champ 'autre note' : absent  - tricherie - notes manquantes" , p))


def headers_table():
    data =[]
    data.append([
              'Noma',
              'Nom',
              'Prénom',
              'Note chiffrée',
              'Autre note',
              'Date de remise'])
    return data


def main_data(tutor, academic_year, session_exam, styles, learning_unit_year, pgm, Contenu):
    p = ParagraphStyle('entete')
    p.alignment = TA_RIGHT
    p.fontSize = 10

    Contenu.append(Spacer(1, 30))
    Contenu.append(Paragraph('Année académique : %s' % str(academic_year), p))
    Contenu.append(Paragraph('Session : %d' % session_exam.number_session, p))
    Contenu.append(Spacer(1, 30))
    Contenu.append(Paragraph("<strong>%s : %s</strong>" % (learning_unit_year.acronym,learning_unit_year.title), styles["Normal"]) )
    Contenu.append(Spacer(1, 30))
    p_tutor = Paragraph('''<b>%s</b>''' % tutor, styles["Normal"])
    data_tutor= [[p_tutor],
       [''],
       [''],
       ['']]
    table_tutor=Table(data_tutor)
    p_pgm = Paragraph('''<b>Programme : %s</b>''' % pgm.acronym, styles["Normal"])
    data_pgm= [[p_pgm   ],
               ['Date de délibération : '],
               ['Président du jury : '],
               ['Secrétaire du jury : '],
              ]
    table_pgm=Table(data_pgm)
    table_pgm.setStyle(TableStyle([

                       ('VALIGN',(0,0), (-1,-1), 'TOP')
                       ]))
    # Contenu.append(Paragraph("Responsable : %s" % tutor, styles["Normal"]) )
    dataTT = [[table_pgm,table_tutor]]

    tt=Table(dataTT)
    tt.setStyle(TableStyle([

                       ('VALIGN',(0,0), (-1,-1), 'TOP')
                       ]))
    Contenu.append(tt)
    Contenu.append(Spacer(1, 12))

def end_page_infos_building(Contenu, styles):
    Contenu.append(Spacer(1, 30))
    p = ParagraphStyle('info')
    p.fontSize = 10
    p.leftIndent = 50
    Contenu.append(Paragraph("Veuillez renvoyer ce formulaire au secrétariat de l'entité gestionnaire" , p))
    Contenu.append(Spacer(1, 30))

    P = Paragraph('''
                <para>
                    <font size=10>Fait à ....................................</font>
                    <br/>
                    <font size=10>Le ..../..../........</font>
                    <br/>
                    <font size=10>Signature</font>
                </para>''',
                styles["BodyText"])
    Contenu.append(P)
