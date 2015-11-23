# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _

class Student_notes_display(models.Model):
    _name = 'osis.student_notes_display'
    _description = "Student notes display"
    _auto = False


    title_learning_unit = fields.Char('Title learning unit')
    # title_offer = fields.Char('Title offer')
    year = fields.Integer('Year')
    session_name = fields.Char('Session name')
    exam_id = fields.Char('Exam id')
    student_name = fields.Char('Student name')
    score = fields.Char('Score')
    student_ref  = fields.Integer('Student ref')
    learning_unit_ref = fields.Integer('Learning unit id')


    def init(self, cr):
        print 'init notes display'
        tools.sql.drop_view_if_exists(cr, 'osis_student_notes_display')
        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes_display AS (
            select ay.year as year,
                   e.session_name as session_name,
                   ee.exam_id as exam_id,
                   p.name as student_name,
                   ee.score as score,
                   luy.learning_unit_id as learning_unit_ref,
                   lue.student_id as student_ref,
                   ee.id as id,
                   lu.title as title_learning_unit
            from osis_exam e join osis_exam_enrollment ee on ee.exam_id = e.id
                 join osis_learning_unit_year luy on e.learning_unit_year_id = luy.id
                 join osis_academic_year ay on luy.academic_year_id = ay.id
                 join osis_learning_unit_enrollment lue on lue.id = ee.learning_unit_enrollment_id
                 join osis_student s on s.id = lue.student_id
                 join osis_person p on s.person_id = p.id
                 join osis_learning_unit lu on luy.learning_unit_id = lu.id
            )''')



    def init_old(self, cr):
        print 'init notes display'
        tools.sql.drop_view_if_exists(cr, 'osis_student_notes_display')
        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes_display AS (
            select o.title as title_offer,
                   ay.year as year,
                   e.session_name as session_name,
                   ee.exam_id as exam_id,
                   p.name as student_name,
                   ee.score as score,
                   luy.learning_unit_id as learning_unit_ref,
                   lue.student_id as student_ref,
                   e.id ,
                   lu.title as title_learning_unit
            from osis_exam e join osis_exam_enrollment ee on ee.exam_id = e.id
                 join osis_learning_unit_year luy on e.learning_unit_year_id = luy.id
                 join osis_academic_year ay on luy.academic_year_id = ay.id
                 join osis_offer_year oy on oy.academic_year_id = ay.id
                 join osis_offer o on oy.offer_id = o.id
                 join osis_learning_unit_enrollment lue on lue.id = ee.learning_unit_enrollment_id
                 join osis_student s on s.id = lue.student_id
                 join osis_person p on s.person_id = p.id
                 join osis_learning_unit lu on luy.learning_unit_id = lu.id
            )''')
