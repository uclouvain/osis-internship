# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _

class Student_notes_display(models.Model):
    _name = 'osis.student_notes_display'
    _description = "Student notes display"
    _auto = False


    title_learning_unit = fields.Char('Title learning unit')
    title_offer = fields.Char('Title offer')
    year = fields.Integer('Year')
    status = fields.Char('Status')
    session_name = fields.Char('Session name')
    exam_id = fields.Char('Exam id')
    student_name = fields.Char('Student name')
    score = fields.Char('Score')
    student_id  = fields.Integer('Student Id')
    learning_unit_id = fields.Integer('Learning unit  id')


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'osis_student_notes_display')
        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes_display AS (
            select status,  osis_learning_unit.title as title_learning_unit, osis_offer.title as title_offer, year, session_name, osis_exam.id as exam_id, osis_person.name as student_name , osis_exam_enrollment.score as score, osis_exam.learning_unit_year_id as id, osis_student.id as student_id, osis_learning_unit.id as learning_unit_id
            from osis_exam , osis_learning_unit, osis_academic_year, osis_exam_enrollment, osis_offer_year, osis_offer ,
                 osis_learning_unit_enrollment, osis_student, osis_person, osis_offer_enrollment
            where osis_offer_year.academic_year_id = osis_academic_year.id
            and osis_exam_enrollment.exam_id=osis_exam.id
            and osis_offer_year.offer_id = osis_offer.id
            and osis_offer_enrollment.offer_year_id = osis_offer_year.id
            and osis_exam_enrollment.learning_unit_enrollment_id = osis_learning_unit_enrollment.id
            and osis_learning_unit_enrollment.student_id = osis_student.id
            and osis_student.person_id = osis_person.id
            and osis_student.id = osis_offer_enrollment.student_id)''')
