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
from io import BytesIO
from io import StringIO
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_JUSTIFY, TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import BaseDocTemplate,SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table,TableStyle,Frame,PageTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from core.models import AcademicCalendar, SessionExam, ExamEnrollment, LearningUnitYear, Person, AcademicYear, OfferYear

PAGE_SIZE = A4
MARGIN_SIZE = 20 * mm
COLS_WIDTH = [25*mm,30*mm,30*mm,25*mm,30*mm,27*mm]
SMALL_INTER_LINE = Spacer(1, 12)
BIG_INTER_LINE = Spacer(1, 30)

def print_notes(request,tutor, academic_year, session_exam,sessions,learning_unit_year_id):
    """
    Create a multi-page document
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="feuillesNotes.pdf"'

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer,
                            pagesize=PAGE_SIZE,
                            rightMargin=MARGIN_SIZE,
                            leftMargin=MARGIN_SIZE,
                            topMargin=72,
                            bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))

    Contenu = []
    #critères
    academic_calendar = AcademicCalendar.find_academic_calendar_by_event_type(academic_year.id,session_exam.number_session)

    if learning_unit_year_id != -1 :
        #par cours
        list_exam_enrollment = ExamEnrollment.find_exam_enrollments(session_exam)
    else:
        if tutor:
            sessions = SessionExam.find_sessions_by_tutor(tutor, academic_year)
        # In case the user is not a tutor we check whether it is member of a faculty.
        elif request.user.groups.filter(name='FAC').exists():
            faculty = ProgrammeManager.find_faculty_by_user(request.user)
            if faculty:
                sessions = SessionExam.find_sessions_by_faculty(faculty, academic_year, session_exam)

        # Calculate the progress of all courses of the tutor.
        list_exam_enrollment = []
        for session in sessions:
            enrollments = list(ExamEnrollment.find_exam_enrollments(session))
            if enrollments:
                list_exam_enrollment = list_exam_enrollment + enrollments

    list_notes_building(session_exam, learning_unit_year_id, academic_year, academic_calendar, tutor, list_exam_enrollment, styles, request.user.groups.filter(name='FAC').exists(), Contenu)

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

    # Release the canvas
    canvas.restoreState()

def header_building(canvas, doc,styles):
    a = Image("core"+ settings.STATIC_URL +"/img/logo_institution.jpg")

    P = Paragraph('''
                    <para align=center spaceb=3>
                        <font size=16>%s</font>
                    </para>''' % (_('Scores transcript')), styles["BodyText"])
    data_header=[[a,'%s' % _('University Catholic Louvain\nLouvain-la-Neuve\nBelgium') ,P],]

    t_header=Table(data_header, [30*mm, 100*mm,50*mm])

    t_header.setStyle(TableStyle([
                    #    ('SPAN',(0,0), (0,-1)),
                       ]))

    w, h = t_header.wrap(doc.width, doc.topMargin)
    t_header.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h)

def list_notes_building(session_exam, learning_unit_year_id, academic_year, academic_calendar, tutor,list_exam_enrollment, styles, isFac, Contenu):
    #liste des notes
    Contenu.append(SMALL_INTER_LINE)
    data = headers_table(styles)

    old_pgm = None
    current_learning_unit_year= None
    for rec_exam_enrollment in list_exam_enrollment:
        if (int(rec_exam_enrollment.learning_unit_enrollment.learning_unit_year.id) == int(learning_unit_year_id)) or int(learning_unit_year_id) == -1:
            student = rec_exam_enrollment.learning_unit_enrollment.student
            o = rec_exam_enrollment.learning_unit_enrollment.offer
            if old_pgm is None:
                old_pgm = o
                current_learning_unit_year = rec_exam_enrollment.learning_unit_enrollment.learning_unit_year
            if o != old_pgm:
                #Autre programme - 1. mettre les critères
                main_data(tutor, academic_year, session_exam, styles, current_learning_unit_year,old_pgm, Contenu)
                #Autre programme - 2. il faut écrire le tableau

                t=Table(data,COLS_WIDTH)
                t.setStyle(TableStyle([
                                   ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,0), (-1,-1), 'TOP')
                                   ]))

                Contenu.append(t)
                #Autre programme - 3. Imprimer légende
                end_page_infos_building(Contenu, styles)
                legend_building(current_learning_unit_year, isFac, Contenu, styles)
                #Autre programme - 4. il faut faire un saut de page
                Contenu.append(PageBreak())
                data = headers_table(styles)
                old_pgm =o
                current_learning_unit_year = rec_exam_enrollment.learning_unit_enrollment.learning_unit_year

            person = Person.find_person(student.person.id)
            score = None
            if not (rec_exam_enrollment.score_final is None):
                if rec_exam_enrollment.learning_unit_enrollment.learning_unit_year.decimal_scores :
                    score = "{0:.2f}".format(rec_exam_enrollment.score_final)
                else:
                    score = "{0:.0f}".format(rec_exam_enrollment.score_final)
            justification = ""
            if rec_exam_enrollment.justification_final:
                justification = dict(ExamEnrollment.JUSTIFICATION_TYPES)[rec_exam_enrollment.justification_final]
            data.append([student.registration_id,
                           person.last_name,
                           person.first_name,
                           score,
                           justification,
                           academic_calendar.end_date.strftime('%d/%m/%Y')
                           ])

    if old_pgm is None:
        pass
    else:
        main_data(tutor, academic_year, session_exam, styles,current_learning_unit_year, old_pgm, Contenu)
        t=Table(data,COLS_WIDTH)
        t.setStyle(TableStyle([
                           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                           ('VALIGN',(0,0), (-1,-1), 'TOP')
                           ]))

        Contenu.append(t)
        end_page_infos_building(Contenu, styles)
        legend_building(current_learning_unit_year, isFac, Contenu, styles)

def legend_building(learning_unit_year, isFac, Contenu, styles):
    Contenu.append(BIG_INTER_LINE)
    Contenu.append(BIG_INTER_LINE)
    p = ParagraphStyle('legend')
    p.textColor = 'grey'
    p.borderColor = 'grey'
    p.borderWidth = 1
    p.alignment = TA_CENTER
    p.fontSize =8
    p.borderPadding = 5
    legend_text = "%s : %s" % (_('Other score legend'), ExamEnrollment.justification_label_authorized(isFac))
    if not(learning_unit_year.decimal_scores):
        legend_text += "<br/><font color=red>%s</font>" % _('UnAuthorized decimal for this activity')

    Contenu.append(Paragraph('''
                            <para>
                                %s
                            </para>
                            ''' % legend_text, p))

def headers_table(styles):
    data =[]
    data.append([Paragraph('''%s''' % _('Registration number'), styles['BodyText']),
                 Paragraph('''%s''' % _('Last name'), styles['BodyText']),
                 Paragraph('''%s''' % _('First name'), styles['BodyText']),
                 Paragraph('''%s''' % _('Numbered score'), styles['BodyText']),
                 Paragraph('''%s''' % _('Other score'), styles['BodyText']),
                 Paragraph('''%s''' % _('End date'), styles['BodyText'])])
    return data

def main_data(tutor, academic_year, session_exam, styles, learning_unit_year, pgm, Contenu):
    Contenu.append(SMALL_INTER_LINE)
    p_structure = ParagraphStyle('entete_structure')
    p_structure.alignment = TA_LEFT
    p_structure.fontSize = 10

    p = ParagraphStyle('entete_droite')
    p.alignment = TA_RIGHT
    p.fontSize = 10

    Contenu.append(Paragraph('%s : %s' % (_('Academic year'), str(academic_year)), p))
    Contenu.append(Paragraph('Session : %d' % session_exam.number_session, p))
    Contenu.append(BIG_INTER_LINE)

    if pgm.structure is not None:
        Contenu.append(Paragraph('%s' % pgm.structure, p_structure))
        Contenu.append(SMALL_INTER_LINE)

    Contenu.append(Paragraph("<strong>%s : %s</strong>" % (learning_unit_year.acronym,learning_unit_year.title), styles["Normal"]) )
    Contenu.append(SMALL_INTER_LINE)

    tutor = None
    if tutor is None:
        p_tutor = Paragraph(''' ''' , styles["Normal"])
    else:
        p_tutor = Paragraph('''<b>%s %s</b>''' % (tutor.person.last_name, tutor.person.first_name), styles["Normal"])

    data_tutor= [[p_tutor],
       [''],
       [''],
       ['']]
    table_tutor=Table(data_tutor)
    p_pgm = Paragraph('''<b>%s : %s</b>''' % (_('Program'),pgm.acronym), styles["Normal"])
    data_pgm= [[p_pgm],
               [_('Deliberation date') + ' : '],
               [_('Chair of the exam board') + ' : '],
               [_('Exam board secretary') + ' : '],
              ]
    table_pgm=Table(data_pgm)
    table_pgm.setStyle(TableStyle([
    ('LEFTPADDING',(0,0),(-1,-1), 0),
                         ('RIGHTPADDING',(0,0),(-1,-1), 0),
                       ('VALIGN',(0,0), (-1,-1), 'TOP')
                       ]))
    # Contenu.append(Paragraph("Responsable : %s" % tutor, styles["Normal"]) )
    dataTT = [[table_pgm,table_tutor]]

    tt=Table(dataTT, colWidths='*')
    tt.setStyle(TableStyle([
        ('LEFTPADDING',(0,0),(-1,-1), 0),
                             ('RIGHTPADDING',(0,0),(-1,-1), 0),
                       ('VALIGN',(0,0), (-1,-1), 'TOP')
                       ]))
    Contenu.append(tt)
    Contenu.append(Spacer(1, 12))

def end_page_infos_building(Contenu, styles):
    Contenu.append(BIG_INTER_LINE)
    p = ParagraphStyle('info')
    p.fontSize = 10
    p.alignment = TA_LEFT
    Contenu.append(Paragraph("Please return this document to the administrative office of the program administrator" , p))
    Contenu.append(BIG_INTER_LINE)
    p_signature = ParagraphStyle('info')
    p_signature.fontSize = 10
    p_signature.leftIndent = 330
    P = Paragraph('''
                    <font size=10>%s ....................................</font>
                    <br/>
                    <font size=10>%s ..../..../........</font>
                    <br/>
                    <font size=10>%s</font>
                ''' % (_('Done at'), _('The'), _('Signature')),
                p_signature)
    Contenu.append(P)
