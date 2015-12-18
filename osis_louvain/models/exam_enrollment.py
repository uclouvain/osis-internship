# -*- coding: utf-8 -*-


from openerp import models, fields, api, _, exceptions

class Exam_enrollment(models.Model):
    _name = 'osis.exam_enrollment'
    _description = "Exam enrollment"
    _sql_constraints = [('exam_enrollment_unique','unique(learning_unit_enrollment_id,session_exam_id)','An exam enrollment must be unique on learning_unit_enrollment/session_exam')]

    session_exam_id = fields.Many2one('osis.session_exam', string='Session exam')
    learning_unit_enrollment_id = fields.Many2one('osis.learning_unit_enrollment', string='Learning unit enrollment')

    date_enrollment = fields.Date('Date enrollment')
    encoding_status = fields.Selection([('SAVED','Saved'),('SUBMITTED','Submitted')])
    score_draft = fields.Float('Score draft')
    score_reencoded = fields.Float('Score reencoded')
    score_final = fields.Float('Score reencoded')
    justification_draft = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
    justification_reencoded = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])
    justification_final = fields.Selection([('ILL',_('Ill')),('ABSENT',_('Absent')),('JUSTIFIED_ABSENCE',_('Justified absence')),('CHEATING',_('Cheating')),('SCORE_MISSING',_('Score missing'))])

    @api.constrains('score_draft', 'score_2', 'score_final')
    def _check_scores(self):
        for record in self:
            if record.score_draft:
                if record.score_draft < 0 or record.score_draft >20:
                    raise exceptions.ValidationError(_("Score must be >= 0 and <=20"))
            if record.score_reencoded:
                if record.score_reencoded < 0 or record.score_reencoded >20:
                    raise exceptions.ValidationError(_("Score must be >= 0 and <=20"))
            if record.score_final:
                if record.score_final < 0 or record.score_final >20:
                    raise exceptions.ValidationError(_("Score must be >= 0 and <=20"))
