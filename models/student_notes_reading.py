# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools, _

class Student_notes_reading(models.Model):
    _name = 'osis.student_notes'
    _description = "Student notes"
    _auto = False


    title = fields.Char('Title')
    year = fields.Integer('Year')
    status = fields.Char('Status')
    session_name = fields.Char('Session name')
    exam_id = fields.Char('Exam id')
    student_name = fields.Char('Student name')
    score = fields.Char('Score')
    student_id  = fields.Integer('Student Id')


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'osis_student_notes')
        cr.execute('''CREATE OR REPLACE VIEW osis_student_notes AS (
            select status,  osis_learning_unit.title as title, year, session_name, osis_exam.id as exam_id, osis_person.name as student_name , osis_exam_enrollment.score as score, osis_exam.learning_unit_year_id as id, osis_student.id as student_id
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


    @api.multi
    def display_students_notes(self):
       #Initialize required parameters for opening the form view of invoice
       #Get the view ref. by paasing module & name of the required form
       view_ref = self.env['ir.model.data'].get_object_reference('osis-louvain', 'student_notes_display_tree_view')
       view_id = view_ref[1] if view_ref else False

       #Let's prepare a dictionary with all necessary info to open create invoice form with
       #customer/client pre-selected
       res = {
           'type': 'ir.actions.act_window',
           'name': _('Customer Invoice'),
           'res_model': 'osis.student_notes_display',
           'view_type': 'tree',
           'view_mode': 'tree',
           'view_id': view_id,
           'target': 'current',
           'res_id':self.student_id,
        #    'context': {'student_id': 1}
       }

       return res
