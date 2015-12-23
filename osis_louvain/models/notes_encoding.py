# -*- coding: utf-8 -*-

from openerp import models, fields, api, _, exceptions

class Notes_encoding(models.Model):
        _name = 'osis.notes_encoding'
        _description = "Notes encoding"
        _sql_constraints = [('notes_encoding_unique','unique(exam_enrollment_id)','A note encoding record must be unique on exam enrollment')]

        score_1 = fields.Float('Score 1')
        justification_1 = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
        score_2 = fields.Float('Score 2')
        justification_2 = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
        score_final = fields.Float('Score Final')
        justification_final = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
        end_date = fields.Date()

        notes_status = fields.Char(compute = '_get_notes_status')
        session_exam_id = fields.Many2one('osis.session_exam', string='Session exam')
        exam_enrollment_id =fields.Many2one('osis.exam_enrollment', string='Exam enrollment', ondelete='cascade')

        student_name = fields.Char(related="exam_enrollment_id.learning_unit_enrollment_id.offer_enrollment_id.student_id.person_id.last_name")
        student_first_name = fields.Char(related="exam_enrollment_id.learning_unit_enrollment_id.offer_enrollment_id.student_id.person_id.first_name")
        student_registration_number = fields.Char(related="exam_enrollment_id.learning_unit_enrollment_id.offer_enrollment_id.student_id.registration_number")
        offer = fields.Char(related="exam_enrollment_id.learning_unit_enrollment_id.offer_enrollment_id.offer_year_id.offer_id.acronym")
        offer_id = fields.Many2one('osis.offer', related="exam_enrollment_id.learning_unit_enrollment_id.offer_enrollment_id.offer_year_id.offer_id")
        encoding_stage_1_done = fields.Boolean('Encoding stage 1 done', default = False)
        double_encoding_done = fields.Boolean('Double encoding done', default = False)
        learning_unit = fields.Char(related="exam_enrollment_id.learning_unit_enrollment_id.learning_unit_year_id.acronym")
        academic_year = fields.Integer(related="exam_enrollment_id.learning_unit_enrollment_id.learning_unit_year_id.academic_year_id.year")
        learning_unit_credits = fields.Float(related="exam_enrollment_id.learning_unit_enrollment_id.learning_unit_year_id.credits")


        @api.multi
        def _get_notes_status(self):
            notes_status = 'NULL'
            for record in self:
                if record.score_1 and record.score_2:
                    if record.score_1 != record.score_2:
                        record.notes_status = 'DIFFERENT'
                    else:
                        record.notes_status = 'EQUAL'
                if record.justification_1 and record.justification_2:
                    if record.justification_1 != record.justification_2:
                        record.notes_status = 'DIFFERENT'
                    else:
                        record.notes_status = 'EQUAL'
                if (record.justification_1 and not record.justification_2) or (record.justification_2 and not record.justification_1):
                    record.notes_status = 'DIFFERENT'


        @api.constrains('score_1', 'score_2', 'score_final')
        def _check_scores(self):
            for record in self:
                if record.score_1:
                    if record.score_1 < 0 or record.score_1 >20:
                        raise exceptions.ValidationError(_("Score must be >= 0 and <=20"))
                if record.score_2:
                    if record.score_2 < 0 or record.score_2 >20:
                        raise exceptions.ValidationError(_("Score must be >= 0 and <=20"))
                if record.score_final:
                    if record.score_final < 0 or record.score_final >20:
                        raise exceptions.ValidationError(_("Score must be >= 0 and <=20"))
