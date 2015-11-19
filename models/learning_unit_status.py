# -*- coding: utf-8 -*-

from openerp import models, fields, api, tools

class Learning_unit_status(models.Model):
    _name = 'osis.status'
    _description = "Learning unit status"
    _order = "acronym"
    _auto = False

    acronym = fields.Char('Title')
    title = fields.Char('Title')
    year = fields.Integer('Year')
    status = fields.Char('Status')
    session_name = fields.Char('Session name')
    exam_id = fields.Char('Exam id')
    learning_unit_enrollment_id =fields.Integer('Learnint unit enrollment id')


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'osis_status')
        cr.execute('''CREATE OR REPLACE VIEW osis_status AS (
            select status, osis_offer.acronym, osis_offer.title, year, session_name, osis_exam.id as exam_id, osis_exam.learning_unit_year_id as id, osis_learning_unit_enrollment.id as learning_unit_enrollment_id
            from osis_exam , osis_learning_unit, osis_exam_enrollment, osis_offer_year, osis_offer, osis_learning_unit_enrollment, osis_offer_enrollment, osis_academic_year, osis_student
            where osis_student.id = osis_offer_enrollment.student_id
            and osis_offer_enrollment.offer_year_id = osis_offer_year.id
            and osis_exam_enrollment.exam_id=osis_exam.id
            and osis_offer_year.offer_id = osis_offer.id
            and osis_learning_unit_enrollment.student_id = osis_student.id
            and osis_exam_enrollment.learning_unit_enrollment_id = osis_learning_unit_enrollment.id
            and osis_academic_year.id = osis_offer_year.academic_year_id)''')


    @api.multi
    def wizard_encode_results(self):

        lue = self.env['osis.learning_unit_enrollment'].search([('id','=',self.learning_unit_enrollment_id)])
        students = self.env['osis.student'].search([('learning_unit_enrollment_id','=',lue.id)])
# exam_enrollment_ids
        wiz_id = self.env['osis.wizard.result'].create({
            'exam_enrollment_id': self.id,
            'line_ids':[(0,0,{'student_id': student.id}) for student in students],
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'osis.wizard.result',
            'res_id': wiz_id.id,
            'target': 'new',
        }

class ExamResults(models.Model):
    _name = 'epc.exam.result'

    exam_enrollment_id = fields.Many2one('epc.exam_enrollment', string='Exam')
    student_id = fields.Many2one('osis.student', string='Student', required=True)
    result = fields.Float('Result')
